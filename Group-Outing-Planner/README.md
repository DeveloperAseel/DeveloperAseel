# طلعة ترضي الشلة | Group Outing Planner

A small Python project with two cooperating agents that plan an outing in Riyadh for two people. The Researcher finds options; the Coordinator checks the plan and requests targeted changes. Both can choose web searches and read discovered pages.

## Requirements

- Python 3.10 or newer. No packages to install; only the standard library is used.
- An OpenAI API key with model access and available billing/credits.
- A Tavily API key with search/extract credits.
- Internet access for live mode. A ChatGPT subscription does not supply API credits.

## Run

### Arabic web interface

The responsive RTL interface includes a two-person preferences form, budget/date/time fields, a plan, review notes and a collaboration log. No frontend packages or build step are needed.

```bash
python server.py
```

Open **http://127.0.0.1:8000** in your browser. This starts in demo mode: examples are fictional and make no API requests.

To enable actual agents, stop the server with Ctrl+C and run:

```bash
python server.py --live
```

Enter both API keys in the terminal's hidden prompts, or provide the environment variables described below. Select **تخطيط فعلي** in the page. Keys stay in server memory and are not sent to the browser or saved. Live requests can incur API charges. The result and collaboration log appear after the run completes, not as a live stream.

If port 8000 is busy, use `python server.py --port 8001` and open the printed URL. Keep this server on your own computer: it is a local development app bound to loopback, not a production hosting setup. GitHub displays the source; opening `index.html` directly or using GitHub Pages alone will not run the Python agents.

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
- `server.py`: local web server, input validation and API routing.
- `index.html`: Arabic responsive frontend, styles and browser interactions.
- `.gitignore`: excludes local secrets and Python caches.
- `README.md`: setup and explanation.

## Interview explanation

> I built a small cooperative agent system for planning group outings. A research agent finds options using web tools, and a coordinator checks the constraints and requests targeted revisions. The agents choose their tool calls based on the available evidence, while the application limits the number of attempts. I distinguish verified information from estimates and explicitly report unresolved constraints.

## Validation

Local checks cover Python syntax, the offline illustration, mocked tool calls, review validation, feedback transfer and the revision limit. The web interface is also checked against the demo API, invalid input and disabled live mode. These checks do not establish live model quality or verify actual venues. A live run requires your own API keys.

## References

- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OpenAI: Chat Completions API](https://developers.openai.com/api/reference/resources/chat)
- [Tavily Search](https://docs.tavily.com/documentation/api-reference/endpoint/search)
- [Tavily Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract)
- [Python local HTTP server](https://docs.python.org/3/library/http.server.html)
