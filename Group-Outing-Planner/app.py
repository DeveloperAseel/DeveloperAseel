"""Streamlit frontend for the two-agent outing planner."""

import datetime
import os

import streamlit as st

from planner import Model, WebTools, plan_outing


st.set_page_config(page_title="طلعة ترضي الشلة", page_icon="🌤️", layout="centered")
st.markdown("""<style>
  .stApp {background: #fffdf9;}
  .stMainBlockContainer {direction: rtl; text-align: right; max-width: 850px;}
  h1, h2, h3, p, label {text-align: right;}
  textarea {direction: rtl; text-align: right;}
  div[data-testid="stForm"] {background: white; border-radius: 20px; padding: 24px;}
  div[data-testid="stText"] {direction: rtl; text-align: right; white-space: pre-wrap;}
</style>""", unsafe_allow_html=True)


def secret(name):
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        return str(st.secrets.get(name, "")).strip()
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return ""


def demo_result(budget, first, second):
    activity, cafe = round(budget * .5, 2), round(budget * .25, 2)
    return {
        "demo": True, "rounds": 2,
        "plan": (f"مثال خيالي لتوضيح النتيجة فقط\n\n"
                 f"١. نشاط تجريبي يناسب: {first}\nتكلفة افتراضية: {activity:g} ريال للشخص.\n\n"
                 f"٢. جلسة تجريبية تناسب: {second}\nتكلفة افتراضية: {cafe:g} ريال للشخص.\n\n"
                 f"المجموع الافتراضي: {activity + cafe:g} ريال للشخص.\n"
                 "لم يتم البحث عن أماكن حقيقية."),
        "review": {"approved": False,
                   "feedback": "تم تعديل المثال ليلتزم بالميزانية؛ يلزم بحث فعلي للتحقق من الأماكن والأوقات.",
                   "uncertainties": ["الأماكن والأسعار افتراضية.", "أوقات العمل والتنقل غير متحققة."]},
        "trace": ["الباحث: اقترح نشاطًا وجلسة تتجاوز تكلفتهما الميزانية.",
                  "المنسّق: طلب نشاطًا أقل تكلفة يناسب رغبات الشخص الأول.",
                  "الباحث: عدّل المثال إلى خيارات ضمن الميزانية.",
                  "المنسّق: سجّل المعلومات التي تحتاج بحثًا فعليًا."]}


st.title("🌤️ طلعة ترضي الشلة")
st.write("قولوا لنا وش تحبّون، والباحث والمنسّق يتعاونون على خطة تناسبكم في الرياض.")
left, right = st.columns(2)
left.info("**الباحث**\n\nيبحث عن الأماكن ويقترح خطة.")
right.info("**المنسّق**\n\nيراجع التفاصيل ويطلب البدائل.")

model_key, search_key = secret("OPENAI_API_KEY"), secret("TAVILY_API_KEY")
mode = st.radio("طريقة التشغيل", ["مثال تجريبي", "تخطيط فعلي"], horizontal=True)
if mode == "مثال تجريبي":
    st.caption("مثال مكتوب مسبقًا، بدون بحث أو نماذج أو أماكن حقيقية.")
elif not model_key or not search_key:
    st.warning("أضيفي مفتاحي OpenAI وTavily في إعدادات الأسرار، مثل ما هو موضح في README.")
else:
    st.caption("بحث فعلي قد يستهلك رصيدًا من الخدمات. لا توجد حجوزات أو تأكيد للتوفر.")

with st.form("outing"):
    c1, c2 = st.columns(2)
    date = c1.date_input("تاريخ الطلعة", datetime.date.today() + datetime.timedelta(days=1))
    budget = c2.number_input("ميزانية كل شخص · ريال", min_value=1, max_value=10000, value=150)
    c1, c2 = st.columns(2)
    start = c1.time_input("من الساعة", datetime.time(18, 0))
    end = c2.time_input("إلى الساعة", datetime.time(22, 0))
    first = st.text_area("الأول وش يحب؟", "نشاط خفيف وتجربة جديدة، بدون زحمة.", max_chars=500)
    second = st.text_area("والثاني وش يحب؟", "قهوة ومكان هادي وجلسة مريحة.", max_chars=500)
    area = st.selectbox("أي جهة في الرياض؟", ["أي جهة", "شمال الرياض", "شرق الرياض", "غرب الرياض", "جنوب الرياض", "وسط الرياض"])
    submitted = st.form_submit_button("رتّبوا طلعتنا", type="primary")

if submitted:
    st.session_state.pop("result", None)
    if not first.strip() or not second.strip():
        st.error("اكتبي رغبات الشخصين أولًا.")
    elif end <= start:
        st.error("وقت النهاية لازم يكون بعد البداية في اليوم نفسه.")
    elif mode == "تخطيط فعلي" and (not model_key or not search_key):
        st.error("التخطيط الفعلي يحتاج مفتاحي الخدمات. تقدرين تجربين المثال بدون مفاتيح.")
    else:
        with st.spinner("الباحث والمنسّق يجهّزون الخطة… قد يستغرق البحث عدة دقائق."):
            try:
                if mode == "مثال تجريبي":
                    result = demo_result(budget, first.strip(), second.strip())
                else:
                    request = (f"الرياض، التاريخ {date.isoformat()}، من {start.strftime('%H:%M')} "
                               f"إلى {end.strftime('%H:%M')}. الميزانية {budget} ريال لكل شخص. "
                               f"رغبات الأول: {first.strip()}. رغبات الثاني: {second.strip()}. المنطقة: {area}.")
                    trace = []
                    result = plan_outing(request, Model(model_key), WebTools(search_key), log=trace.append)
                    result.update(demo=False, trace=trace)
                result["summary"] = f"{date.isoformat()} · {start.strftime('%H:%M')}–{end.strftime('%H:%M')} · {budget} ريال للشخص · {area}"
                st.session_state.result = result
            except (RuntimeError, ValueError, KeyError, IndexError, TypeError):
                st.error("تعذّر إكمال الخطة. تحققي من الاتصال ورصيد المفاتيح وصلاحية النموذج، ثم حاولي مرة ثانية.")

if "result" in st.session_state:
    result = st.session_state.result
    st.divider()
    st.subheader("خطة طلعتكم")
    st.caption(result["summary"])
    if result["demo"]:
        st.info("مثال خيالي فقط؛ لم يتم البحث عن أماكن حقيقية.")
    elif result["review"]["approved"]:
        st.success("اجتازت مراجعة المنسّق. تأكدوا من التفاصيل قبل الخروج.")
    else:
        st.warning("خطة أولية لم تجتز المراجعة؛ بقيت نقاط تحتاج تحققًا.")
    st.text(result["plan"])
    st.subheader("ملاحظات المنسّق")
    st.text(result["review"]["feedback"])
    for item in result["review"]["uncertainties"]:
        st.text("• " + item)
    with st.expander(f"كيف تعاون الوكيلان؟ · {result['rounds']} جولات"):
        for entry in result["trace"]:
            st.text(entry)
    st.download_button("حمّلي الخطة", result["summary"] + "\n\n" + result["plan"] + "\n\n" +
                       result["review"]["feedback"] + "\n" + "\n".join(result["review"]["uncertainties"]),
                       file_name="outing-plan.txt", mime="text/plain")

st.caption("مشروع Aseel Alsaad · تأكدوا من الأسعار والأوقات قبل الطلعة.")
