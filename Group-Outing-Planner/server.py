"""Local web interface. Run python server.py or python server.py --live."""

import argparse
import datetime
import getpass
import json
import math
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

from planner import Model, WebTools, plan_outing


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("بيانات الطلب غير صحيحة.")
    result = {}
    for field in ("date", "start", "end", "person1", "person2", "area"):
        value = data.get(field, "")
        if not isinstance(value, str) or len(value) > 500:
            raise ValueError("تأكدي من طول وصحة الحقول.")
        result[field] = value.strip()
    if not result["person1"] or not result["person2"]:
        raise ValueError("اكتبي رغبات الشخصين.")
    datetime.date.fromisoformat(result["date"])
    start = datetime.time.fromisoformat(result["start"])
    end = datetime.time.fromisoformat(result["end"])
    if end <= start:
        raise ValueError("وقت النهاية لازم يكون بعد البداية في اليوم نفسه.")
    budget = data.get("budget")
    if isinstance(budget, bool):
        raise ValueError("الميزانية غير صحيحة.")
    try:
        result["budget"] = float(budget)
    except (TypeError, ValueError):
        raise ValueError("اكتبي ميزانية صحيحة.") from None
    if not math.isfinite(result["budget"]) or not 1 <= result["budget"] <= 10000:
        raise ValueError("الميزانية لازم تكون بين 1 و10000 ريال للشخص.")
    result["mode"] = data.get("mode", "demo")
    if result["mode"] not in ("demo", "live"):
        raise ValueError("اختاري وضع تشغيل صحيح.")
    return result


def example_result(data):
    budget = data["budget"]
    activity, cafe = round(budget * .5, 2), round(budget * .25, 2)
    total = round(activity + cafe, 2)
    return {
        "demo": True, "rounds": 2,
        "plan": (f"مثال توضيحي خيالي — {data['date']}، من {data['start']} إلى {data['end']}\n\n"
                 f"١. نشاط تجريبي يناسب: {data['person1']}\nتكلفة افتراضية: {activity:g} ريال للشخص.\n\n"
                 f"٢. جلسة تجريبية تناسب: {data['person2']}\nتكلفة افتراضية: {cafe:g} ريال للشخص.\n\n"
                 f"المجموع الافتراضي: {total:g} ريال للشخص، من ميزانية {budget:g} ريال.\n"
                 "لم يتم البحث عن أماكن حقيقية. هذا المثال يوضح شكل النتيجة فقط."),
        "review": {"approved": False,
                   "feedback": "عدّل الباحث المثال ليلتزم بالميزانية؛ الأماكن والأوقات لم تُتحقق فعليًا.",
                   "uncertainties": ["الأماكن والأسعار افتراضية.", "أوقات العمل والتنقل تحتاج بحثًا في الوضع الفعلي."]},
        "trace": ["الباحث: اقترح نشاطًا وجلسة بتكلفة تتجاوز الميزانية.",
                  "المنسّق: طلب بديلًا أقل تكلفة مع الحفاظ على رغبات الشخصين.",
                  "الباحث: عدّل المثال إلى نشاط وجلسة ضمن الميزانية.",
                  "المنسّق: سجّل المعلومات التي تحتاج تحققًا قبل اعتماد الخطة."]}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def respond(self, code, data, content_type="application/json; charset=utf-8"):
        body = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def allowed_host(self):
        port = self.server.server_port
        return self.headers.get("Host") in {f"127.0.0.1:{port}", f"localhost:{port}"}

    def do_GET(self):
        if not self.allowed_host():
            self.respond(403, {"error": "استخدمي رابط الخادم المحلي."})
        elif self.path in ("/", "/index.html"):
            self.respond(200, Path(__file__).with_name("index.html").read_bytes(), "text/html; charset=utf-8")
        elif self.path == "/api/config":
            self.respond(200, {"live_enabled": bool(self.server.model_key and self.server.search_key)})
        else:
            self.respond(404, {"error": "الصفحة غير موجودة."})

    def do_POST(self):
        origin = self.headers.get("Origin")
        expected_origin = "http://" + self.headers.get("Host", "")
        if not self.allowed_host() or (origin and origin != expected_origin):
            self.respond(403, {"error": "الطلب لازم يجي من الصفحة المحلية."})
            return
        if self.path != "/api/plan":
            self.respond(404, {"error": "المسار غير موجود."})
            return
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            self.respond(415, {"error": "الطلب لازم يكون JSON."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 12000:
                raise ValueError("حجم الطلب غير صحيح.")
            self.connection.settimeout(10)
            data = validate(json.loads(self.rfile.read(length)))
        except (ValueError, UnicodeDecodeError, TimeoutError) as error:
            self.respond(400, {"error": "تأكدي من التاريخ والأوقات والحقول. " + str(error)})
            return
        if not self.server.plan_lock.acquire(blocking=False):
            self.respond(409, {"error": "فيه خطة قيد التجهيز؛ انتظري لين تخلص."})
            return
        try:
            if data["mode"] == "demo":
                result = example_result(data)
            elif not self.server.model_key or not self.server.search_key:
                self.respond(503, {"error": "الوضع الفعلي يحتاج تشغيل الخادم مع --live ومفاتيح الخدمات."})
                return
            else:
                request = (f"المدينة: الرياض. التاريخ: {data['date']}. الوقت: {data['start']}–{data['end']}. "
                           f"ميزانية الشخص: {data['budget']:g} ريال. رغبات الأول: {data['person1']}. "
                           f"رغبات الثاني: {data['person2']}. المنطقة المفضلة: {data['area'] or 'أي منطقة'}.")
                trace = []
                result = plan_outing(request, Model(self.server.model_key),
                                     WebTools(self.server.search_key), log=trace.append)
                result.update(demo=False, trace=trace)
            self.respond(200, result)
        except (RuntimeError, ValueError, KeyError, IndexError, TypeError):
            self.respond(502, {"error": "تعذّر إكمال الخطة. تحققي من الاتصال ورصيد المفاتيح وصلاحية النموذج، ثم حاولي مرة ثانية."})
        finally:
            self.server.plan_lock.release()


def main():
    parser = argparse.ArgumentParser(description="Local Group Outing Planner web app")
    parser.add_argument("--live", action="store_true", help="Enable real agents; prompt for missing API keys")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    model_key = search_key = ""
    if args.live:
        model_key = (os.getenv("OPENAI_API_KEY") or getpass.getpass("OpenAI API key (hidden): ")).strip()
        search_key = (os.getenv("TAVILY_API_KEY") or getpass.getpass("Tavily API key (hidden): ")).strip()
        if not model_key or not search_key:
            parser.error("Both keys are required for --live.")
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        server.model_key, server.search_key = model_key, search_key
        server.plan_lock = Lock()
        print(f"Open http://127.0.0.1:{server.server_port} — {'live + demo' if args.live else 'demo'}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
