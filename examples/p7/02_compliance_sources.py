"""P7 lab 02 companion: official sources ledger, US first (checked_on per row; 2026-11-04 / 2026-11-08).
Learning only — NOT legal advice. Rules change; verify current official text.
"""
from __future__ import annotations
import json
from pathlib import Path
from _common import DATA

# checked_on records when the author read each page; this script never fetches.
SOURCES = [
  {
    "id": "sec_15c3_5",
    "title": "17 CFR 240.15c3-5 Market Access Rule",
    "issuer": "SEC / eCFR",
    "jurisdiction": "US",
    "source_url": "https://www.ecfr.gov/current/title-17/chapter-II/part-240/subject-group-ECFRc8401dcba174f73/section-240.15c3-5",
    "checked_on": "2026-11-04",
    "effective_from": "see source",
    "status": "in force per source text on checked_on",
    "summary": "Pre-trade credit/capital & erroneous-order controls; regulatory controls; exclusive BD control; ≥annual review + CEO cert."
  },
  {
    "id": "reg_sho_201",
    "title": "17 CFR 242.201 Regulation SHO circuit breaker",
    "issuer": "SEC / eCFR",
    "jurisdiction": "US",
    "source_url": "https://www.ecfr.gov/current/title-17/chapter-II/part-242/subject-group-ECFR1607681c7b4f78d/section-242.201",
    "checked_on": "2026-11-04",
    "effective_from": "see source",
    "status": "in force per source text on checked_on",
    "summary": "10% decline from prior-day listing-market close → short sale ≤ NBB restricted for rest of day + next day."
  },
  {
    "id": "finra_4210",
    "title": "FINRA Rule 4210 Margin Requirements",
    "issuer": "FINRA",
    "jurisdiction": "US",
    "source_url": "https://www.finra.org/rules-guidance/rulebooks/finra-rules/4210",
    "checked_on": "2026-11-04",
    "effective_from": "see source",
    "status": "in force per source text on checked_on",
    "summary": "Current rule text includes IML / intraday margin deficit definitions (a)(17)-(19) and (d)(2)."
  },
  {
    "id": "finra_26_10",
    "title": "Regulatory Notice 26-10 (intraday margin replaces PDT)",
    "issuer": "FINRA",
    "jurisdiction": "US",
    "source_url": "https://www.finra.org/rules-guidance/notices/26-10",
    "checked_on": "2026-11-08",
    "effective_from": "2026-06-04",
    "status": "adopted; effective; member phase-in to 2027-10-20",
    "summary": "Published 2026-04-20; effective 2026-06-04; phase-in to 2027-10-20; replaces pattern day trader count + $25,000 minimum equity with intraday margin standards."
  },
  {
    "id": "finra_26_11",
    "title": "Regulatory Notice 26-11 (IMD/IML interpretations for intraday margin)",
    "issuer": "FINRA",
    "jurisdiction": "US",
    "source_url": "https://www.finra.org/rules-guidance/notices/26-11",
    "checked_on": "2026-11-04",
    "effective_from": "2026-06-04",
    "status": "in force per source text on checked_on",
    "summary": "Published 2026-05-19; effective 2026-06-04. Publishes Rule 4210 interpretations for new intraday margin: IML (intraday margin level) and IMD (intraday margin deficit = abs of largest negative IML). Deletes obsolete PDT day-trading interpretations. PDF: https://www.finra.org/sites/default/files/2026-05/Regulatory-Notice-26-11.pdf"
  },
  {
    "id": "finra_15_09",
    "title": "Regulatory Notice 15-09 Algorithmic trading supervision",
    "issuer": "FINRA",
    "jurisdiction": "US",
    "source_url": "https://www.finra.org/rules-guidance/notices/15-09",
    "checked_on": "2026-11-04",
    "effective_from": "see source",
    "status": "in force per source text on checked_on",
    "summary": "Published 2015-03-26; five practice areas; references SEA 15c3-5 and Reg SHO."
  },
  {
    "id": "sec_cftc_2025_09_02",
    "title": "SEC-CFTC Joint Staff Statement (Project Crypto / Crypto Sprint)",
    "issuer": "SEC TM + CFTC DMO/DCR staff",
    "jurisdiction": "US (crypto)",
    "source_url": "https://www.sec.gov/newsroom/speeches-statements/sec-cftc-project-crypto-090225",
    "checked_on": "2026-11-04",
    "effective_from": "see source",
    "status": "staff statement (non-binding)",
    "summary": "Staff statement 2025-09-02 (not Commission rule); view that law does not prohibit registered exchanges facilitating certain spot crypto products; explicitly non-binding."
  },
  {
    "id": "sec_withdraw_pda_2025_06",
    "title": "Withdrawal of Proposed Regulatory Actions (incl. PDA conflicts S7-12-23)",
    "issuer": "SEC / Federal Register",
    "jurisdiction": "US",
    "source_url": "https://www.federalregister.gov/documents/2025/06/17/2025-11110/withdrawal-of-proposed-regulatory-actions",
    "checked_on": "2026-11-04",
    "effective_from": "see source",
    "status": "proposal withdrawn",
    "summary": "Published 2025-06-17; formally withdraws several 2022–2023 proposals including Conflicts of Interest Associated With the Use of Predictive Data Analytics by Broker-Dealers and Investment Advisers (File No. S7-12-23; 88 FR 53960). Withdrawal ≠ absence of remaining duties under Advisers Act / Reg BI / firm policies. Not legal advice."
  },
  {
    "id": "sec_fy2026_exam_priorities",
    "title": "SEC Division of Examinations FY2026 Priorities — Emerging Financial Technology / AI",
    "issuer": "SEC Division of Examinations",
    "jurisdiction": "US",
    "source_url": "https://www.sec.gov/about/reports-publications/2026-examination-priorities",
    "checked_on": "2026-11-04",
    "effective_from": "see source",
    "status": "in force per source text on checked_on",
    "summary": "Published/updated 2025-11-17. Emerging FinTech focus: automated investment tools, AI, trading algorithms/platforms, alt-data. Exams check fair/accurate AI representations; ops vs disclosures; algo advice vs investor profiles; policies to supervise AI in fraud/AML/trading/back-office. Complements PDA-conflicts proposal withdrawal (S7-12-23) — withdrawal ≠ no remaining duties. Not legal advice; date-stamp official pages.",
    "pdf": "https://www.sec.gov/files/2026-exam-priorities.pdf"
  },
  {
    "id": "finra_2026_genai_agents",
    "title": "FINRA 2026 Annual Regulatory Oversight Report — GenAI / AI Agents (NEW FOR 2026)",
    "issuer": "FINRA",
    "jurisdiction": "US",
    "source_url": "https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report/gen-ai",
    "checked_on": "2026-11-04",
    "effective_from": "see source",
    "status": "in force per source text on checked_on",
    "summary": "GenAI section NEW FOR 2026. Rules (incl. FINRA Rule 3110 Supervision) remain technology-neutral. Emerging Agents: autonomy, scope/authority, auditability, data sensitivity, domain knowledge, reward misalignment, plus GenAI bias/hallucination/privacy. Consider human-in-the-loop, access/data monitoring, action logging, guardrails. Awareness only — not legal advice.",
    "report": "https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report"
  },
  {
    "id": "sec_t1_bulletin",
    "title": "New “T+1” Settlement Cycle — Investor Bulletin",
    "issuer": "SEC OIEA / Investor.gov",
    "jurisdiction": "US",
    "source_url": "https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/new-t1-settlement-cycle-what-investors-need-know-investor-bulletin",
    "checked_on": "2026-11-08",
    "effective_from": "2024-05-28 (compliance date)",
    "status": "in force",
    "summary": "Most applicable securities transactions settle in one business day after trade date (T+1)."
  },
  {
    "id": "luld_plan",
    "title": "Limit Up-Limit Down Plan (Amendment 20 text; Amendment 18 removed opening doubling)",
    "issuer": "LULD Plan Participants",
    "jurisdiction": "US",
    "source_url": "https://www.luldplan.com/",
    "pdf": "https://cdn.luldplan.com/plans/LULD-Plan-Amendment-20.pdf",
    "checked_on": "2026-11-08",
    "effective_from": "Amendment 18: 2020-02-24",
    "status": "in force",
    "summary": "Single-stock dynamic bands (5-min reference price), Tier1 5% / Tier2 10% above $3; 15-s limit state -> pause; regular hours only."
  },
  {
    "id": "sec_regsho_page",
    "title": "Key Points About Regulation SHO",
    "issuer": "SEC",
    "jurisdiction": "US",
    "source_url": "https://www.sec.gov/investor/pubs/regsho.htm",
    "checked_on": "2026-11-08",
    "effective_from": "see source",
    "status": "educational page; its T+2 passages are outdated (see T+1 bulletin)",
    "summary": "Rules 200 marking, 201 price test, 203(b) locate, 204 close-out; short seller pays dividends to lender; unlimited-loss risk."
  },
  {
    "id": "finra_21_23",
    "title": "Regulatory Notice 21-23 Best Execution / PFOF",
    "issuer": "FINRA",
    "jurisdiction": "US",
    "source_url": "https://www.finra.org/rules-guidance/notices/21-23",
    "checked_on": "2026-11-08",
    "effective_from": "see source",
    "status": "guidance",
    "summary": "Rule 5310 best execution is not concerned solely with price; NBBO is a reference."
  },
  {
    "id": "reg_nms_611_proposal",
    "title": "Proposed rescission of Reg NMS Rules 611 and 610(e) (S7-2026-20)",
    "issuer": "SEC",
    "jurisdiction": "US",
    "source_url": "https://www.sec.gov/rules-regulations/2026/06/s7-2026-20",
    "checked_on": "2026-11-08",
    "effective_from": "n/a",
    "status": "Proposed (Release 34-105655); Rule 611 still in eCFR",
    "summary": "Proposal only; do not write “repealed”."
  },
  {
    "id": "usc_78i",
    "title": "Securities Exchange Act Section 9(a) — 15 U.S.C. 78i (wash trades, matched orders, manipulative series)",
    "issuer": "US Code (govinfo, 2023 edition)",
    "jurisdiction": "US",
    "source_url": "https://www.govinfo.gov/content/pkg/USCODE-2023-title15/html/USCODE-2023-title15-chap2B-sec78i.htm",
    "checked_on": "2026-11-10",
    "effective_from": "see source",
    "status": "compared with current US Code through PL 119-138 (uscode.house.gov /us/usc/119-138/t15/s78i/): §78i(a) matches the 2023 edition; last amendment 2010 (PL 111-203)",
    "summary": "9(a)(1): no-change-in-beneficial-ownership trades / matched orders to create a false appearance of active trading; 9(a)(2): series of transactions to induce others. Wash TRADE (manipulation) != wash SALE (tax). Not legal advice."
  },
  {
    "id": "finra_5210",
    "title": "FINRA Rule 5210 Supplementary Material .02 (self-trades) and .03 (disruptive quoting and trading)",
    "issuer": "FINRA",
    "jurisdiction": "US",
    "source_url": "https://www.finra.org/rules-guidance/rulebooks/finra-rules/5210",
    "checked_on": "2026-11-10",
    "effective_from": "2017-04-03 (SR-FINRA-2017-004)",
    "status": "in force per source text on checked_on",
    "summary": "Unintentional self-trades generally bona fide, but firms must review for and prevent a pattern from a single or related algorithms; .03 Type 1 (layer one side, trade other side, cancel) and Type 2 (inside-NBBO order, trade against joiners); cross-venue patterns count."
  },
  {
    "id": "sec_2026_37_cat_review",
    "title": "SEC press release 2026-37 — concept release on the Consolidated Audit Trail (CAT) review",
    "issuer": "SEC",
    "jurisdiction": "US",
    "source_url": "https://www.sec.gov/newsroom/press-releases/2026-37-sec-seeks-public-comment-consolidated-audit-trail-other-audit-trails-data-sources",
    "checked_on": "2026-11-10",
    "effective_from": "n/a",
    "status": "concept release (2026-04-16); review not concluded",
    "summary": "Comprehensive review of CAT (funding/cost, regulatory purpose, structure/governance, design/scope). CAT exists under Rule 613 (adopted 2012-07-11). Do not predict the outcome."
  },
  {
    "id": "sec_34_106402_innovation_exemption",
    "title": "SEC Release 34-106402 (File 4-927) — Innovation Exemption order: TSVs exempt from 'exchange', Covered Firms from 'dealer' (tokenized NMS stock)",
    "issuer": "SEC",
    "jurisdiction": "US",
    "source_url": "https://www.sec.gov/files/rules/exorders/2026/34-106402.pdf",
    "checked_on": "2026-11-10",
    "effective_from": "2026-09-17",
    "status": "temporary conditional exemptive order; effective 2026-09-17 until 2031-09-17 (section V); 91 FR 60168 (2026-09-22); no comment closing date set, SEC still accepting comments on checked_on",
    "summary": "Section 36(a)(1) exemptions. Conditions incl. symbol/volume limits by LULD tier (Tier 1: 75 symbols, 0.25% of that stock's prior-month ADV; Tier 2: 250 symbols, 2.5%), same rights as traditional stock, synthetics excluded, issuer notice/objection for third-party tokens, public auditable smart contracts on a public permissionless ledger, halt with primary listing exchange, USD transaction data (UTC times), TSV not subject to Reg NMS. Not a final rule; no venue recommended; not legal advice.",
    "fr": "https://www.federalregister.gov/documents/2026/09/22/2026-19388/order-granting-temporary-conditional-exemptive-relief-pursuant-to-section-36a1-of-the-securities"
  },
  {
    "id": "sec_atkins_innovation_exemption_2026",
    "title": "Chairman Atkins — Statement on the Innovation Exemption (2026-09-17)",
    "issuer": "SEC",
    "jurisdiction": "US",
    "source_url": "https://www.sec.gov/newsroom/speeches-statements/atkins-innovation-exemption-bridge-toward-durable-rulemaking-091726",
    "checked_on": "2026-11-10",
    "effective_from": "n/a",
    "status": "commissioner statement (explains the order; not the order itself)",
    "summary": "Key conditions as stated: TSV must be a U.S. person and comply with OFAC sanctions; permissioned access; no synthetics, tokens carry the same rights incl. dividends and voting; issuers can object. Anti-fraud/anti-manipulation provisions apply in full."
  },
  {
    "id": "sec_uyeda_innovation_exemption_2026",
    "title": "Commissioner Uyeda — Statement on the Innovation Exemption (2026-09-17)",
    "issuer": "SEC",
    "jurisdiction": "US",
    "source_url": "https://www.sec.gov/newsroom/speeches-statements/uyeda-statement-innovation-exemption-091726",
    "checked_on": "2026-11-10",
    "effective_from": "n/a",
    "status": "commissioner statement (explains the order; not the order itself)",
    "summary": "Symbol limits and volume caps calibrated by LULD tiers; USD transaction data (price, size, time, pool address, end-of-day pool size, daily volume) public at regular intervals."
  },
  {
    "id": "irs_w8ben",
    "title": "Instructions for Form W-8BEN",
    "issuer": "IRS",
    "jurisdiction": "US tax (cross-border)",
    "source_url": "https://www.irs.gov/instructions/iw8ben",
    "checked_on": "2026-11-08",
    "effective_from": "see source",
    "status": "current instructions",
    "summary": "Given to the withholding agent, not the IRS; 30% on certain US-source income unless reduced by treaty."
  },
  {
    "id": "us_china_treaty",
    "title": "US–China Income Tax Treaty (Art. 9 dividends)",
    "issuer": "IRS",
    "jurisdiction": "US/CN treaty",
    "source_url": "https://www.irs.gov/pub/irs-trty/china.pdf",
    "checked_on": "2026-11-08",
    "effective_from": "see treaty",
    "status": "in force per IRS page",
    "summary": "Source-state tax on dividends to a beneficial owner resident in the other state shall not exceed 10% of gross; conditions apply."
  },
  {
    "id": "irc_1091",
    "title": "26 U.S.C. §1091 Wash sales",
    "issuer": "US House OLRC",
    "jurisdiction": "US tax",
    "source_url": "https://uscode.house.gov/us/usc/119-124/t26/s1091/",
    "checked_on": "2026-11-08",
    "effective_from": "see statute",
    "status": "in force",
    "summary": "30 days before to 30 days after the sale (61 calendar days incl. sale date); loss deduction limited."
  },
  {
    "id": "fred_terms",
    "title": "FRED® Services Terms of Use",
    "issuer": "Federal Reserve Bank of St. Louis",
    "jurisdiction": "US (data licence)",
    "source_url": "https://fred.stlouisfed.org/legal/",
    "checked_on": "2026-11-08",
    "effective_from": "see source",
    "status": "current terms",
    "summary": "API prohibitions include ML/AI development or training (k) and storing/caching/archiving (l); general prohibition (p)."
  },
  {
    "id": "cn_iit_law",
    "title": "中华人民共和国个人所得税法",
    "issuer": "全国人大 / 上海税务公开页",
    "jurisdiction": "CN tax (cross-border)",
    "source_url": "https://shanghai.chinatax.gov.cn/zcfw/zcfgk/grsds/201809/t441789.html",
    "checked_on": "2026-11-08",
    "effective_from": "see law",
    "status": "in force",
    "summary": "183-day resident test; 20% proportional rate for dividends and property transfer; foreign tax credit capped (Art. 7)."
  },
  {
    "id": "cn_mof_sat_2020_3",
    "title": "财政部 税务总局公告2020年第3号（境外所得）",
    "issuer": "MOF / SAT",
    "jurisdiction": "CN tax (cross-border)",
    "source_url": "https://www.gov.cn/zhengce/zhengceku/2020-01/22/content_5471604.htm",
    "checked_on": "2026-11-08",
    "effective_from": "see source",
    "status": "in force",
    "summary": "Separate computation; credit within limit; excess carried 5 years; file 1 Mar–30 Jun next year."
  },
  {
    "id": "cn_crs",
    "title": "金融账户涉税信息自动交换（CRS）",
    "issuer": "国家税务总局",
    "jurisdiction": "CN tax (cross-border)",
    "source_url": "https://www.chinatax.gov.cn/chinatax/aeoi_index.html",
    "checked_on": "2026-11-08",
    "effective_from": "see source",
    "status": "framework page",
    "summary": "Due diligence + annual reporting + exchange between authorities; differs from US FATCA."
  },
  {
    "id": "safe_sh_2026",
    "title": "国家外汇管理局上海市分局 FAQ（2026，5万美元便利化额度）",
    "issuer": "SAFE Shanghai",
    "jurisdiction": "CN FX (cross-border)",
    "source_url": "https://www.safe.gov.cn/shanghai/2026/0402/2412.html",
    "checked_on": "2026-11-08",
    "effective_from": "see source",
    "status": "FAQ",
    "summary": "Annual facilitation quota USD 50,000 per person for FX purchase/settlement."
  },
  {
    "id": "safe_sx_2018",
    "title": "国家外汇管理局陕西省分局 FAQ（证券投资用途）",
    "issuer": "SAFE Shaanxi",
    "jurisdiction": "CN FX (cross-border)",
    "source_url": "https://www.safe.gov.cn/shaanxi/2018/1204/249.html",
    "checked_on": "2026-11-08",
    "effective_from": "see source",
    "status": "FAQ (narrow conclusion only)",
    "summary": "Quota FX purchase remitted abroad needs a genuine current-account purpose, which does not include overseas securities investment."
  },
  {
    "id": "csrc_2024_8",
    "title": "证券市场程序化交易管理规定（试行）",
    "issuer": "CSRC / 中国证监会公告〔2024〕8号",
    "jurisdiction": "CN (A-share comparison)",
    "source_url": "https://www.gov.cn/gongbao/2024/issue_11426/202406/content_6959680.html",
    "checked_on": "2026-11-04",
    "effective_from": "2024-10-08",
    "status": "in force per source text on checked_on",
    "summary": "Effective 2024-10-08; programmatic trading = computer-generated/routed orders; report-before-trade; exchange sets abnormal thresholds; HFT features delegated to exchanges."
  },
  {
    "id": "csrc_2025_12_futures",
    "title": "期货市场程序化交易管理规定（试行）",
    "issuer": "CSRC / 中国证监会公告〔2025〕12号",
    "jurisdiction": "CN (A-share comparison)",
    "source_url": "https://www.gov.cn/gongbao/2025/issue_12226/202508/content_7036966.html",
    "checked_on": "2026-11-04",
    "effective_from": "2025-10-09",
    "status": "in force per source text on checked_on",
    "summary": "Published 2025-06-13; effective 2025-10-09. Futures programmatic trading: report-before-trade (customer→FC→exchange confirm); HFT standards set by futures exchanges; host-colocation/seat rules; abnormal cancel/replace monitoring. Companion official page: https://www.csrc.gov.cn/csrc/c100028/c7564353/content.shtml"
  },
  {
    "id": "sse_faq_2025_04_03",
    "title": "上交所就正式发布程序化交易管理实施细则答记者问",
    "issuer": "SSE",
    "jurisdiction": "CN (A-share comparison)",
    "source_url": "https://www.sse.com.cn/aboutus/mediacenter/hotandd/c/c_20250403_10776805.shtml",
    "checked_on": "2026-11-04",
    "effective_from": "2025-07-07",
    "status": "in force per source text on checked_on",
    "summary": "细则自2025-07-07施行; 高频认定: 单账户每秒申报撤单合计最高≥300笔, 或全日≥20000笔; 四类异常行为构成要件说明."
  },
  {
    "id": "szse_细则_pdf",
    "title": "深圳证券交易所程序化交易管理实施细则",
    "issuer": "SZSE 深证上〔2025〕292号",
    "jurisdiction": "CN (A-share comparison)",
    "source_url": "https://docs.static.szse.cn/www/lawrules/rule/trade/current/W020250403603802169453.pdf",
    "checked_on": "2026-11-04",
    "effective_from": "2025-07-07",
    "status": "in force per source text on checked_on",
    "summary": "自2025-07-07施行; 第33条高频: 每秒≥300笔或单日≥20000笔; 第18条四类异常监控类型."
  },
  {
    "id": "szse_release_notice",
    "title": "关于发布《深圳证券交易所程序化交易管理实施细则》的通知",
    "issuer": "SZSE",
    "jurisdiction": "CN (A-share comparison)",
    "source_url": "https://www.szse.cn/lawrules/rule/trade/current/t20250403_612770.html",
    "checked_on": "2026-11-04",
    "effective_from": "2025-07-07",
    "status": "in force per source text on checked_on",
    "summary": "发布日2025-04-03; 施行2025-07-07."
  },
  {
    "id": "pbc_2021_237",
    "title": "关于进一步防范和处置虚拟货币交易炒作风险的通知 银发〔2021〕237号",
    "issuer": "PBoC et al. / www.gov.cn",
    "jurisdiction": "CN (crypto)",
    "source_url": "https://www.gov.cn/zhengce/zhengceku/2021-10/08/content_5641404.htm",
    "checked_on": "2026-11-04",
    "effective_from": "see source",
    "status": "in force per source text on checked_on",
    "summary": "Dated 2021-09-15; virtual currency not legal tender; related businesses illegal financial activities; offshore exchanges serving PRC residents likewise prohibited."
  },
  {
    "id": "hkex_nb_program_trading_2026",
    "title": "Northbound Program Trading Reporting (Stock Connect)",
    "issuer": "HKEX / SSE / SZSE",
    "jurisdiction": "HK/CN (comparison)",
    "source_url": "https://www.hkex.com.hk/Mutual-Market/Stock-Connect/Reference-Materials/Northbound-Program-Trading-Reporting?sc_lang=en",
    "checked_on": "2026-11-04",
    "effective_from": "2026-01-12",
    "status": "in force per source text on checked_on",
    "summary": "Mainland NB Program Trading Reporting Requirements effective 2026-01-12; ECP submissions from 2026-01-12; existing investors transition to 2026-04-10; thresholds include automation / fast order rate / many stocks+turnover / customized software (SSE/SZSE separate)."
  },
  {
    "id": "sfc_24ec55",
    "title": "Circular to licensed corporations — Use of generative AI language models (24EC55)",
    "issuer": "SFC Hong Kong",
    "jurisdiction": "HK (comparison)",
    "source_url": "https://apps.sfc.hk/edistributionWeb/gateway/EN/circular/doc?refNo=24EC55",
    "checked_on": "2026-11-04",
    "effective_from": "2024-11-12",
    "status": "in force per source text on checked_on",
    "summary": "Issued 2024-11-12, immediate effect. Risk-based Core Principles for GenAI LMs; investment recommendations/advice/research = high-risk → human-in-the-loop + validation/monitoring/disclosures. Asia peer to FINRA GenAI themes. Awareness not license; not legal advice."
  },
  {
    "id": "esma74_algo_briefing_2026",
    "title": "ESMA Supervisory Briefing on Algorithmic Trading in the EU (ESMA74-1505669079-10311)",
    "issuer": "ESMA",
    "jurisdiction": "EU (comparison)",
    "source_url": "https://www.esma.europa.eu/document/supervisory-briefing-algorithmic-trading-eu",
    "checked_on": "2026-11-04",
    "effective_from": "see source",
    "status": "non-binding briefing",
    "summary": "Published 2026-02-26. Non-binding supervisory briefing (Art.29(2) ESMA Reg; not comply-or-explain). Algo definition: human click/authorisation ≠ out-of-scope if algorithm determined parameters. Material change retest incl. ML retrain/adaptive capabilities. Stress: 2× prior-6m peak messages/trades. PTC hard blocks mandatory / soft recommended. Outsourcing: firm remains liable. AI Act interaction + RTS 6 Art.9 annual self-assessment spirit. Literacy + Asia peers (SFC 24EC55 / FINRA GenAI); NOT a license checklist; not HFT how-to; not legal advice.",
    "pdf": "https://www.esma.europa.eu/sites/default/files/2026-02/ESMA74-1505669079-10311_Supervisory_Briefing_on_Algorithmic_Trading_in_the_EU.pdf"
  }
]

print("=== official sources ledger (US first; comparisons labelled) ===")
print("NOT LEGAL/TAX ADVICE. This script prints a LOCAL ledger; it does NOT fetch URLs.")
print("checked_on = date the author read the page; re-check the official text before relying on it.")
for s in SOURCES:
    print(f"[{s['jurisdiction']}] {s['id']}: {s['title']}")
    print(f"    {s['source_url']}")
    print(f"    checked_on={s['checked_on']} effective_from={s['effective_from']} status={s['status']}")
    print(f"    summary: {s['summary']}")
Path(DATA / "official_sources.json").write_text(json.dumps(SOURCES, ensure_ascii=False, indent=2))
print("saved", DATA / "official_sources.json")
us = sum(s["jurisdiction"].startswith("US") for s in SOURCES)
print(f"n_sources={len(SOURCES)} us_first_block={us} fields_complete={all(all(k in s for k in ('source_url','checked_on','effective_from','status','jurisdiction')) for s in SOURCES)}")
