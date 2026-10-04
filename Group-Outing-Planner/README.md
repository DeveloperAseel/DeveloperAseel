# طلعة ترضي الشلة | Group Outing Planner

A small Python project with two cooperating agents that plan an outing in Riyadh for two people. The Researcher finds options; the Coordinator checks the plan and requests targeted changes. Both can choose web searches and read discovered pages.

## Requirements

- Python 3.10 or newer and Streamlit (the only external package).
- An OpenAI API key with model access and available billing/credits.
- A Tavily API key with search/extract credits.
- Internet access for live mode. A ChatGPT subscription does not supply API credits.

## Run

### Arabic web interface

The Streamlit interface includes a two-person preferences form, budget/date/time fields, a plan, review notes, a collaboration log and a text download. No HTML or JavaScript files are needed.

Download this folder and open a terminal in it:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally **http://localhost:8501**). The default is **مثال تجريبي**: examples are fictional and make no API requests.

To enable actual agents, create a local `.streamlit` folder inside this project folder and a `secrets.toml` file in it:

```toml
OPENAI_API_KEY = "your-openai-key"
TAVILY_API_KEY = "your-tavily-key"
```

Use your actual keys only in your local secrets file, never in committed code. This file is excluded by `.gitignore`. Restart Streamlit and select **تخطيط فعلي** in the page. You can also use environment variables instead of a secrets file. The app reads keys on the server and never displays them in the page. Live requests can incur API charges. The result and collaboration log appear after the run completes, not as a live stream.

Results are kept in the current Streamlit session and can be downloaded; they are not written to a database. If you edit the form after running, the displayed summary identifies the previous request until you submit again. Refreshing the browser may reset the session. GitHub displays the source; it does not host the running Streamlit app. For a local-only binding, add `--server.address 127.0.0.1` to the run command.

### Command-line interface

Download this folder, open a terminal in it, then run:

```bash
python planner.py --demo
```

This is a **scripted offline illustration**, not a model run. It uses fictional options to show a budget conflict and revision. It needs no keys and makes no network requests.

For the actual agents:

```bash
python planner.py
```

Enter your request in Arabic or English, including the date, time window, two people's preferences and budget per person. Example:

> الرياض، 15 أكتوبر 2026، من 6 إلى 10 مساءً. الأول يبي نشاط خفيف، والثاني يبي مكان هادي. الميزانية 150 ريال لكل شخص، ونفضل شمال الرياض.

The program prompts for keys with hidden input and does not save them. Alternatively, set `OPENAI_API_KEY` and `TAVILY_API_KEY` as environment variables. Never put keys in the code or commit them. The program does not load `.env` files.

The default model is `gpt-4.1-mini`; optionally set `OPENAI_MODEL` to another Chat Completions model supporting function calling and the parameters used here.

## How the agents cooperate

1. **Researcher:** chooses search queries and pages, compares options and drafts a schedule with source links.
2. **Coordinator:** independently uses tools to check the constraints and evidence, then returns a structured review.
3. When rejected, the Researcher gets the review and investigates specific gaps or alternatives. The Coordinator reviews again.
4. Stop after approval or two revisions. An unresolved plan is explicitly labeled preliminary.

The outer review cycle is programmed. Inside each turn, the model chooses whether to search, which query to use, which page to read and when it has enough evidence. Both roles can use the same model; they have different instructions and separate message histories. This is a small cooperative agent workflow, not a fully autonomous travel service.

### Tools and limits

- `search_web`: Tavily Search, up to four sources per query.
- `read_page`: Tavily Extract, only for URLs returned by search during the run.
- At most four tool rounds and one final model response per agent turn, with at most two tool calls in a round. Three planning/review rounds maximum, up to 30 model requests and 48 search/extract requests in the worst case; most runs should use fewer.
- Terminal shows tool names, drafts and review feedback so cooperation is visible.

## Output and limitations

The output is an Arabic schedule with venue links, suitability explanations, supported costs and remaining uncertainties. Prices and hours can change; a model's approval is not a guarantee. Pages may be inaccessible or incomplete. There is no mapping or booking API: travel times must be labeled estimates, and reservations/availability are not confirmed. Insufficient evidence should produce an unapproved preliminary plan.

Live mode sends your outing request to OpenAI and search queries/selected URLs to Tavily. Keep inputs to ordinary preferences and do not include private personal details. Usage can cost money depending on the providers' current plans, model and number of calls. Check your provider dashboards for limits and usage.

## Files

- `planner.py`: both agents, tools, revision loop and offline illustration.
- `app.py`: Streamlit interface, validation and session results.
- `requirements.txt`: Streamlit dependency.
- `.gitignore`: excludes local secrets and Python caches.
- `README.md`: setup and explanation.

## Interview explanation

> I built a small cooperative agent system for planning group outings. A research agent finds options using web tools, and a coordinator checks the constraints and requests targeted revisions. The agents choose their tool calls based on the available evidence, while the application limits the number of attempts. I distinguish verified information from estimates and explicitly report unresolved constraints.

## Validation

Local checks cover Python syntax, the offline illustration, mocked tool calls, review validation, feedback transfer and the revision limit. Streamlit AppTest checks the form, demo output, session persistence, invalid input and missing credentials. These checks do not establish live model quality or verify actual venues. A live run requires your own API keys.

## References

- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OpenAI: Chat Completions API](https://developers.openai.com/api/reference/resources/chat)
- [Tavily Search](https://docs.tavily.com/documentation/api-reference/endpoint/search)
- [Tavily Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract)
- [Streamlit forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form)
- [Streamlit session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
- [Streamlit secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
