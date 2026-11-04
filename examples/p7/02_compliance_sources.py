"""P7 lab 02 companion: official sources checklist with fetch status (checked 2026-11-04).
Learning only — NOT legal advice. Rules change; verify current official text.
"""
from __future__ import annotations
import json
from pathlib import Path
from _common import DATA

# Status reflects fetches performed this session by the authoring agent.
SOURCES = [
  {
    "id": "csrc_2024_8",
    "title": "证券市场程序化交易管理规定（试行）",
    "issuer": "CSRC / 中国证监会公告〔2024〕8号",
    "url": "https://www.gov.cn/gongbao/2024/issue_11426/202406/content_6959680.html",
    "fetch": "OK",
    "verified": "Effective 2024-10-08; programmatic trading = computer-generated/routed orders; report-before-trade; exchange sets abnormal thresholds; HFT features delegated to exchanges.",
  },
  {
    "id": "csrc_2025_12_futures",
    "title": "期货市场程序化交易管理规定（试行）",
    "issuer": "CSRC / 中国证监会公告〔2025〕12号",
    "url": "https://www.gov.cn/gongbao/2025/issue_12226/202508/content_7036966.html",
    "fetch": "OK",
    "verified": "Published 2025-06-13; effective 2025-10-09. Futures programmatic trading: report-before-trade (customer→FC→exchange confirm); HFT standards set by futures exchanges; host-colocation/seat rules; abnormal cancel/replace monitoring. Companion official page: https://www.csrc.gov.cn/csrc/c101954/c7564346/content.shtml",
  },
  {
    "id": "sse_faq_2025_04_03",
    "title": "上交所就正式发布程序化交易管理实施细则答记者问",
    "issuer": "SSE",
    "url": "https://www.sse.com.cn/aboutus/mediacenter/hotandd/c/c_20250403_10776805.shtml",
    "fetch": "OK",
    "verified": "细则自2025-07-07施行; 高频认定: 单账户每秒申报撤单合计最高≥300笔, 或全日≥20000笔; 四类异常行为构成要件说明.",
  },
  {
    "id": "szse_细则_pdf",
    "title": "深圳证券交易所程序化交易管理实施细则",
    "issuer": "SZSE 深证上〔2025〕292号",
    "url": "https://docs.static.szse.cn/www/lawrules/rule/trade/current/W020250403603802169453.pdf",
    "fetch": "OK",
    "verified": "自2025-07-07施行; 第33条高频: 每秒≥300笔或单日≥20000笔; 第18条四类异常监控类型.",
  },
  {
    "id": "szse_release_notice",
    "title": "关于发布《深圳证券交易所程序化交易管理实施细则》的通知",
    "issuer": "SZSE",
    "url": "https://www.szse.cn/lawrules/rule/trade/current/t20250403_612770.html",
    "fetch": "OK",
    "verified": "发布日2025-04-03; 施行2025-07-07.",
  },
  {
    "id": "sec_15c3_5",
    "title": "17 CFR 240.15c3-5 Market Access Rule",
    "issuer": "SEC / eCFR",
    "url": "https://www.ecfr.gov/current/title-17/chapter-II/part-240/subject-group-ECFRc8401dcba174f73/section-240.15c3-5",
    "fetch": "OK",
    "verified": "Pre-trade credit/capital & erroneous-order controls; regulatory controls; exclusive BD control; ≥annual review + CEO cert.",
  },
  {
    "id": "reg_sho_201",
    "title": "17 CFR 242.201 Regulation SHO circuit breaker",
    "issuer": "SEC / eCFR",
    "url": "https://www.ecfr.gov/current/title-17/chapter-II/part-242/subject-group-ECFR1607681c7b4f78d/section-242.201",
    "fetch": "OK",
    "verified": "10% decline from prior-day listing-market close → short sale ≤ NBB restricted for rest of day + next day.",
  },
  {
    "id": "finra_4210",
    "title": "FINRA Rule 4210 Margin Requirements",
    "issuer": "FINRA",
    "url": "https://www.finra.org/rules-guidance/rulebooks/finra-rules/4210",
    "fetch": "OK",
    "verified": "Current rule text includes IML / intraday margin deficit definitions (a)(17)-(19) and (d)(2).",
  },
  {
    "id": "finra_26_10",
    "title": "Regulatory Notice 26-10 (intraday margin replaces PDT)",
    "issuer": "FINRA",
    "url": "https://www.finra.org/rules-guidance/notices/26-10",
    "fetch": "OK",
    "verified": "Published 2026-04-20; effective 2026-06-04; phase-in to 2027-10-20; replaces pattern day trader count + $25,000 minimum equity with intraday margin standards.",
  },
  {
    "id": "finra_26_11",
    "title": "Regulatory Notice 26-11 (IMD/IML interpretations for intraday margin)",
    "issuer": "FINRA",
    "url": "https://www.finra.org/rules-guidance/notices/26-11",
    "fetch": "OK",
    "verified": "Published 2026-05-19; effective 2026-06-04. Publishes Rule 4210 interpretations for new intraday margin: IML (intraday margin level) and IMD (intraday margin deficit = abs of largest negative IML). Deletes obsolete PDT day-trading interpretations. PDF: https://www.finra.org/sites/default/files/2026-05/Regulatory-Notice-26-11.pdf",
  },
  {
    "id": "finra_15_09",
    "title": "Regulatory Notice 15-09 Algorithmic trading supervision",
    "issuer": "FINRA",
    "url": "https://www.finra.org/rules-guidance/notices/15-09",
    "fetch": "OK",
    "verified": "Published 2015-03-26; five practice areas; references SEA 15c3-5 and Reg SHO.",
  },
  {
    "id": "pbc_2021_237",
    "title": "关于进一步防范和处置虚拟货币交易炒作风险的通知 银发〔2021〕237号",
    "issuer": "PBoC et al. / www.gov.cn",
    "url": "https://www.gov.cn/zhengce/zhengceku/2021-10/08/content_5641404.htm",
    "fetch": "OK",
    "verified": "Dated 2021-09-15; virtual currency not legal tender; related businesses illegal financial activities; offshore exchanges serving PRC residents likewise prohibited.",
  },
  {
    "id": "sec_cftc_2025_09_02",
    "title": "SEC-CFTC Joint Staff Statement (Project Crypto / Crypto Sprint)",
    "issuer": "SEC TM + CFTC DMO/DCR staff",
    "url": "https://www.sec.gov/newsroom/speeches-statements/sec-cftc-project-crypto-090225",
    "fetch": "OK",
    "verified": "Staff statement 2025-09-02 (not Commission rule); view that law does not prohibit registered exchanges facilitating certain spot crypto products; explicitly non-binding.",
  },
]

print("=== official sources checklist (checked Asia/Shanghai 2026-11-04) ===")
print("NOT LEGAL ADVICE — rules change; re-read the current official text before acting.")
for s in SOURCES:
    print(f"[{s['fetch']}] {s['id']}: {s['title']}")
    print(f"    {s['url']}")
    print(f"    verified: {s['verified']}")
Path(DATA / "official_sources.json").write_text(json.dumps(SOURCES, ensure_ascii=False, indent=2))
print("saved", DATA / "official_sources.json")
print(f"n_sources={len(SOURCES)} all_fetch_OK={all(s['fetch']=='OK' for s in SOURCES)}")
