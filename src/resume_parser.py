import re, spacy, pdfplumber, docx
from pathlib import Path

SKILLS_DB = [
    # -- programming languages --
    "python","java","javascript","typescript","c++","c#","c","ruby","go","golang",
    "rust","swift","kotlin","scala","r","matlab","perl","php","bash","shell",
    "powershell","dart","lua","haskell","elixir","erlang","clojure","groovy",
    "objective-c","assembly","fortran","cobol","vb.net","visual basic","delphi",
    "julia","f#","ocaml","solidity","vhdl","verilog","sas","abap","apex",

    # -- web frontend --
    "html","css","html5","css3","react","angular","angularjs","vue","svelte",
    "next.js","nuxt.js","remix","gatsby","tailwind","tailwind css","bootstrap",
    "material ui","mui","chakra ui","ant design","jquery","webpack","vite",
    "parcel","rollup","babel","sass","scss","less","styled-components","redux",
    "redux toolkit","mobx","zustand","recoil","pwa","web components","three.js",
    "d3.js","chart.js","framer motion","storybook","web accessibility","wcag",
    "responsive design","cross-browser testing","ajax","json","xml","web sockets",

    # -- backend / frameworks --
    "node.js","django","django rest framework","flask","fastapi","spring",
    "spring boot","express","express.js","nestjs","rails","ruby on rails",
    "laravel","symfony","asp.net","asp.net core",".net",".net core","gin",
    "fiber","echo","actix","axum","phoenix","koa","hapi","strapi","graphql",
    "apollo","rest","restful","grpc","soap","websocket","microservices",
    "serverless","api gateway","api design","openapi","swagger",

    # -- databases --
    "sql","mysql","postgresql","sqlite","mongodb","cassandra","redis",
    "elasticsearch","dynamodb","oracle","oracle db","microsoft sql server",
    "mariadb","couchdb","neo4j","firestore","supabase","cockroachdb",
    "influxdb","timescaledb","realm","database design","database normalization",
    "indexing","query optimization","stored procedures","plsql","t-sql",

    # -- data engineering / big data --
    "hadoop","spark","pyspark","apache spark","kafka","apache kafka","airflow",
    "apache airflow","dbt","snowflake","bigquery","redshift","databricks",
    "hive","pig","flink","apache flink","nifi","apache nifi","luigi","etl",
    "elt","data pipeline","data warehousing","data modeling","data lake",
    "data engineering","stream processing","batch processing",

    # -- cloud / devops / infra --
    "aws","azure","gcp","google cloud","amazon web services","microsoft azure",
    "ec2","s3","lambda","cloudformation","eks","ecs","fargate","azure devops",
    "docker","kubernetes","k8s","helm","terraform","pulumi","ansible","puppet",
    "chef","vagrant","jenkins","ci/cd","github actions","gitlab ci","circleci",
    "travis ci","argo cd","prometheus","grafana","datadog","splunk","new relic",
    "nagios","elk stack","logstash","kibana","nginx","apache","haproxy","istio",
    "linux","unix","windows server","shell scripting","infrastructure as code",
    "site reliability engineering","sre","load balancing","cloud architecture",
    "cloud security","vpc","iam",

    # -- version control / collaboration --
    "git","github","gitlab","bitbucket","svn","mercurial","jira","confluence",
    "trello","asana","notion","slack","agile","scrum","kanban","waterfall",
    "devops","devsecops","tdd","bdd","oop","object oriented programming",
    "functional programming","design patterns","clean code","solid principles",
    "code review","pair programming","version control",

    # -- data science / ml / ai --
    "machine learning","deep learning","nlp","natural language processing",
    "computer vision","reinforcement learning","tensorflow","pytorch","keras",
    "scikit-learn","pandas","numpy","scipy","matplotlib","seaborn","plotly",
    "xgboost","lightgbm","catboost","spacy","nltk","gensim","opencv",
    "transformers","statistics","probability","linear algebra","calculus",
    "data analysis","data visualization","data cleaning","data mining",
    "feature engineering","time series analysis","a/b testing","hypothesis testing",
    "bayesian statistics","regression analysis","classification","clustering",
    "cnn","rnn","lstm","gru","gan","autoencoder","transformer architecture",
    "random forest","decision trees","svm","support vector machine",
    "gradient boosting","ensemble learning","dimensionality reduction","pca",
    "anomaly detection","recommendation systems","mlops","model deployment",
    "model monitoring","mlflow","kubeflow","sagemaker","vertex ai","azure ml",
    "weights and biases","wandb","onnx","tensorrt","quantization",

    # -- generative ai / llm stack --
    "llm","large language model","generative ai","genai","rag",
    "retrieval augmented generation","langchain","langgraph","llamaindex",
    "mcp","model context protocol","ollama","huggingface","hugging face",
    "faiss","pinecone","chromadb","weaviate","milvus","qdrant",
    "vector database","vector search","embeddings","prompt engineering",
    "fine-tuning","lora","qlora","rlhf","openai","openai api","chatgpt",
    "gemini","mistral","llama","claude","anthropic api","agentic ai",
    "ai agents","multi-agent systems","autogpt","crewai","semantic kernel",
    "cosine similarity","tf-idf","bag of words","word2vec","bert","gpt",
    "named entity recognition","ner","sentiment analysis","text classification",
    "topic modeling","speech recognition","text to speech","diffusion models",
    "stable diffusion","image generation",

    # -- bi / analytics tools --
    "tableau","power bi","looker","looker studio","qlik","excel",
    "advanced excel","google sheets","vba","google analytics","mixpanel",
    "amplitude","segment","metabase","superset",

    # -- mobile development --
    "flutter","react native","swiftui","android","android studio","ios",
    "xcode","kotlin multiplatform","jetpack compose","xamarin","ionic",
    "cordova","mobile app development",

    # -- security --
    "cybersecurity","penetration testing","ethical hacking","network security",
    "application security","owasp","vulnerability assessment","siem",
    "cryptography","oauth","oauth2","jwt","saml","sso","ssl/tls","firewall",
    "ids/ips","burp suite","metasploit","wireshark","nmap","kali linux",
    "identity and access management","zero trust",

    # -- testing / qa --
    "unit testing","integration testing","end to end testing","selenium",
    "cypress","playwright","jest","mocha","chai","pytest","junit","testng",
    "postman","soapui","load testing","jmeter","gatling","manual testing",
    "automation testing","test case design","quality assurance","qa",

    # -- blockchain / web3 --
    "blockchain","smart contracts","hardhat","truffle","web3.js",
    "ethers.js","ethereum","web3","nft","defi","cryptocurrency","metamask",

    # -- other tools / misc --
    "vs code","visual studio","intellij","eclipse","figma","sketch",
    "adobe xd","adobe photoshop","adobe illustrator","canva","vercel",
    "netlify","firebase","heroku","render","digitalocean","linode","wordpress",
    "shopify","webflow","zapier","power automate","sap","salesforce","servicenow",
    "unity","unreal engine","game development","3d modeling","blender","autocad",
    "word","powerpoint","excel vba","microsoft office","google workspace",
    "arduino","raspberry pi","iot","embedded systems","robotics","ros",
    "matlab simulink","plc programming","cad",

    # -- project management / methodology --
    "project management","product management","program management","pmp",
    "prince2","six sigma","lean","okr","roadmapping","stakeholder management",
    "risk management","budgeting","resource planning","sprint planning",

    # -- soft skills --
    "communication","leadership","teamwork","problem solving",
    "critical thinking","time management","adaptability","collaboration",
    "creativity","decision making","conflict resolution","negotiation",
    "presentation skills","public speaking","mentoring","analytical skills",
    "attention to detail","work ethic","self motivated","interpersonal skills",
    "emotional intelligence","customer service","multitasking",

    # -- api / architecture --
    "api","event driven architecture","domain driven design",
    "distributed systems","system design","high availability","scalability",
    "caching","message queues","rabbitmq","activemq","zeromq","pub/sub",
]

# Aliases/synonyms that resolve to a canonical SKILLS_DB entry. This lets a resume
# saying "ML" and a JD saying "Machine Learning" match instead of silently missing
# each other because they used different phrasing for the same skill.
SKILL_ALIASES = {
    # -- languages / core --
    "ml": "machine learning", "dl": "deep learning",
    "js": "javascript", "ts": "typescript", "cpp": "c++", "c plus plus": "c++",
    "csharp": "c#", "c sharp": "c#", "py": "python", "golang lang": "golang",
    "objective c": "objective-c", "vb": "visual basic", "powershell scripting": "powershell",

    # -- frontend --
    "nodejs": "node.js", "node": "node.js", "expressjs": "express",
    "express js": "express", "reactjs": "react", "react.js": "react",
    "react js": "react", "vuejs": "vue", "vue.js": "vue", "vue js": "vue",
    "nextjs": "next.js", "next js": "next.js", "nuxtjs": "nuxt.js",
    "angular.js": "angularjs", "angular 2+": "angular", "tailwindcss": "tailwind",
    "tailwind.css": "tailwind css", "material-ui": "mui", "materialui": "mui",
    "scss/sass": "scss", "html/css": "html", "web development": "web components",
    "single page application": "pwa", "spa": "pwa",

    # -- backend --
    "nest.js": "nestjs", "ruby on rails (ror)": "ruby on rails", "ror": "ruby on rails",
    "dotnet": ".net", "dot net": ".net", "asp.net mvc": "asp.net",
    "restful api": "rest", "restful apis": "rest", "rest api": "rest",
    "rest apis": "rest", "web api": "api", "apis": "api",
    "django rest": "django rest framework", "drf": "django rest framework",

    # -- databases --
    "postgres": "postgresql", "psql": "postgresql", "mongo": "mongodb",
    "mongo db": "mongodb", "mssql": "microsoft sql server",
    "sql server": "microsoft sql server", "ms sql": "microsoft sql server",
    "oracle database": "oracle db", "elastic search": "elasticsearch",
    "dynamo db": "dynamodb", "firebase firestore": "firestore",
    "pl/sql": "plsql", "nosql": "mongodb",

    # -- data / big data --
    "apache hadoop": "hadoop", "py spark": "pyspark", "apache kafka": "kafka",
    "apache airflow": "airflow", "apache spark": "spark", "apache hive": "hive",
    "apache flink": "flink", "apache nifi": "nifi",

    # -- cloud / devops --
    "amazon web services": "aws", "microsoft azure": "azure",
    "google cloud platform": "gcp", "amazon ec2": "ec2", "amazon s3": "s3",
    "aws lambda": "lambda", "ci cd": "ci/cd", "cicd": "ci/cd",
    "continuous integration": "ci/cd", "continuous deployment": "ci/cd",
    "github action": "github actions", "gitlab-ci": "gitlab ci",
    "infra as code": "infrastructure as code", "iac": "infrastructure as code",
    "k8s cluster": "kubernetes", "docker compose": "docker",
    "elk": "elk stack", "elastic stack": "elk stack",

    # -- vcs / collab --
    "git hub": "github", "git lab": "gitlab", "bit bucket": "bitbucket",
    "jira software": "jira", "oops": "oop", "object oriented programming": "oop",
    "object-oriented programming": "oop", "fp": "functional programming",

    # -- ml / ai --
    "scikit learn": "scikit-learn", "sklearn": "scikit-learn",
    "tensor flow": "tensorflow", "py torch": "pytorch",
    "computer vision (cv)": "computer vision", "cv": "computer vision",
    "nlp (natural language processing)": "natural language processing",
    "natural language processing (nlp)": "natural language processing",
    "deep neural network": "deep learning", "dnn": "deep learning",
    "artificial intelligence": "machine learning", "ai": "machine learning",
    "a/b test": "a/b testing", "ab testing": "a/b testing",
    "time series": "time series analysis", "ts analysis": "time series analysis",
    "pca analysis": "pca", "svm classifier": "svm",
    "support vector machines": "support vector machine",
    "ml ops": "mlops", "weights & biases": "wandb", "w&b": "wandb",

    # -- genai / llm --
    "genai": "generative ai", "gen ai": "generative ai", "gen-ai": "generative ai",
    "llms": "llm", "large language models": "large language model",
    "retrieval-augmented generation": "retrieval augmented generation",
    "llama index": "llamaindex", "model context protocol (mcp)": "mcp",
    "hugging face": "huggingface", "huggingface transformers": "transformers",
    "vector db": "vector database", "vector dbs": "vector database",
    "finetuning": "fine-tuning", "fine tuning": "fine-tuning",
    "gpt-4": "gpt", "gpt4": "gpt", "chat gpt": "chatgpt",
    "named entity recognition (ner)": "named entity recognition",
    "sentiment analysis (nlp)": "sentiment analysis",

    # -- bi --
    "powerbi": "power bi", "power-bi": "power bi", "ms excel": "excel",
    "microsoft excel": "excel", "google analytics 4": "google analytics", "ga4": "google analytics",

    # -- mobile --
    "react-native": "react native", "reactnative": "react native",
    "android dev": "android", "ios dev": "ios", "jetpack": "jetpack compose",

    # -- security --
    "pen testing": "penetration testing", "pentest": "penetration testing",
    "pentesting": "penetration testing", "app security": "application security",
    "network sec": "network security", "infosec": "cybersecurity",
    "information security": "cybersecurity", "ssl": "ssl/tls", "tls": "ssl/tls",
    "iam policies": "identity and access management",

    # -- testing --
    "unit test": "unit testing", "integration test": "integration testing",
    "e2e testing": "end to end testing", "e2e": "end to end testing",
    "test automation": "automation testing", "jest.js": "jest",

    # -- blockchain --
    "web3js": "web3.js", "ethersjs": "ethers.js", "smart contract": "smart contracts",

    # -- misc tools --
    "vscode": "vs code", "visual studio code": "vs code", "intellij idea": "intellij",
    "adobe ps": "adobe photoshop", "photoshop": "adobe photoshop",
    "illustrator": "adobe illustrator", "sql server management studio": "microsoft sql server",
    "ms word": "word", "unity3d": "unity", "unreal": "unreal engine",
    "iot devices": "iot", "embedded c": "embedded systems",

    # -- pm / methodology --
    "project mgmt": "project management", "product mgmt": "product management",
    "scrum master": "scrum", "agile methodology": "agile", "agile methodologies": "agile",
    "six-sigma": "six sigma",

    # -- soft skills --
    "problem-solving": "problem solving", "team work": "teamwork",
    "time-management": "time management", "critical-thinking": "critical thinking",
    "self-motivated": "self motivated", "public-speaking": "public speaking",
    "analytical skill": "analytical skills", "interpersonal skill": "interpersonal skills",

    # -- architecture --
    "message queue": "message queues", "pub sub": "pub/sub",
    "event-driven architecture": "event driven architecture",
    "ddd": "domain driven design", "system design & architecture": "system design",
}

def _load_spacy():
    for m in ("en_core_web_lg","en_core_web_md","en_core_web_sm"):
        try: return spacy.load(m)
        except OSError: continue
    raise RuntimeError("No spaCy model found.")

NLP = _load_spacy()

# ── text extraction ──────────────────────────────────────────────────────────

def extract_text_from_pdf(path):
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: text.append(t)
    return "\n".join(text)

def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text(path):
    ext = Path(path).suffix.lower()
    if ext == ".pdf":   return extract_text_from_pdf(path)
    if ext in (".docx",".doc"): return extract_text_from_docx(path)
    with open(path,"r",errors="ignore") as f: return f.read()

# ── hyperlink extraction (URLs embedded as clickable links, not visible text) ─

def extract_hyperlinks_from_pdf(path):
    """pdfplumber text extraction misses hyperlinks that show as icons/buttons.
    Pull them directly from page annotations. Includes mailto: links since the
    visible text next to an email icon is often just the icon glyph itself,
    with the real address only present in the link target."""
    links = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                for annot in (page.annots or []):
                    uri = annot.get("uri") or annot.get("URI") or ""
                    if uri and (uri.startswith("http") or uri.startswith("mailto:")):
                        links.append(uri)
    except Exception:
        pass
    return links

def extract_hyperlinks_from_docx(path):
    """DOCX stores hyperlinks in document relationships, not paragraph text."""
    links = []
    try:
        doc = docx.Document(path)
        for rel in doc.part.rels.values():
            if "hyperlink" in rel.reltype.lower():
                target = rel._target
                if isinstance(target, str) and (target.startswith("http") or target.startswith("mailto:")):
                    links.append(target)
    except Exception:
        pass
    return links

def get_extra_urls(path):
    ext = Path(path).suffix.lower()
    if ext == ".pdf":           return extract_hyperlinks_from_pdf(path)
    if ext in (".docx",".doc"): return extract_hyperlinks_from_docx(path)
    return []

# ── contact extractors ───────────────────────────────────────────────────────

# PDF icon fonts (FontAwesome-style) often extract as literal ligature words glued
# directly onto the following text with no space, e.g. "Envelopejohn@gmail.com" or
# "MailContactjohn@x.com". Strip these known icon-label prefixes off the local part.
_EMAIL_ICON_PREFIXES = [
    "envelope", "email", "mail", "contactmail", "gmailicon", "phone-alt", "phonealt",
    "mobile", "contact", "linkedin", "github", "website", "portfolio",
    "location", "address", "leetcode",
]

def extract_email(text):
    for m in re.finditer(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text):
        local, domain = m.group(0).split("@", 1)
        low = local.lower()
        for prefix in _EMAIL_ICON_PREFIXES:
            if low.startswith(prefix) and len(low) > len(prefix):
                local = local[len(prefix):]
                low = local.lower()
        local = local.lstrip("._-")
        if local:
            return f"{local}@{domain}"
    return None

def extract_phone(text):
    m = re.search(
        r"(?:\+?\d{1,3}[\s\-.]?)?(?:\(?\d{2,4}\)?[\s\-.]?)?\d{3,4}[\s\-.]?\d{4}", text)
    return m.group(0).strip() if m else None

# Non-profile GitHub paths to ignore (org pages, feature pages, etc.)
_GH_IGNORE = {"features","marketplace","topics","explore","pricing","about",
               "contact","team","organizations","orgs","settings","pulls",
               "issues","sponsors","readme"}

def extract_linkedin(text):
    """Match linkedin.com/in/username in any URL format, including hyperlinks."""
    # Normalise backslashes that sometimes appear after PDF text extraction
    text = text.replace("\\", "/")
    # Match http://linkedin.com/in/user, www.linkedin.com/in/user, linkedin.com/in/user
    m = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/([\w\-\.%]{2,60})/?",
        text, re.I)
    if m:
        return "linkedin.com/in/" + m.group(1).rstrip("/")
    return None

def extract_github(text):
    """Match github.com/username, skipping non-profile paths."""
    text = text.replace("\\", "/")
    m = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/([\w\-]{1,39})(?:/[\w\-\.]*)?(?:\s|$|[,;\)])",
        text, re.I)
    if m:
        user = m.group(1)
        if user.lower() not in _GH_IGNORE:
            return "github.com/" + user
    # Fallback: simpler pattern without trailing context requirement
    m = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/([\w\-]{1,39})",
        text, re.I)
    if m:
        user = m.group(1)
        if user.lower() not in _GH_IGNORE:
            return "github.com/" + user
    return None

# Words/phrases that show up on line 1-3 of many templates but are NOT a person's name
_NAME_BLACKLIST = {
    "resume","cv","curriculum vitae","bio-data","biodata","profile","portfolio",
    "personal details","contact","contact information","address","summary",
    "objective","career objective","professional summary",
}
_NAME_JUNK_RE = re.compile(r"[@#|•<>\[\]{}]|https?://|www\.|\d{2,}")

def _looks_like_name(candidate):
    if not candidate:
        return False
    c = candidate.strip().strip(":-•").strip()
    if not c or c.lower() in _NAME_BLACKLIST:
        return False
    if _NAME_JUNK_RE.search(c):
        return False
    words = [w for w in c.split() if w]
    if not (1 < len(words) <= 5):
        return False
    # every word should look name-like: starts with a letter, mostly alphabetic
    for w in words:
        core = w.strip(".,")
        if not core or not core[0].isalpha():
            return False
        if not re.match(r"^[A-Za-z][A-Za-z\.\-']*$", core):
            return False
    # avoid picking up an all-lowercase sentence fragment
    if c == c.lower() and len(words) > 2:
        return False
    return True

def extract_name_spacy(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    head_lines = lines[:15]

    # 1) Ask spaCy for PERSON entities near the top of the document, then validate
    #    each candidate so we don't accidentally return a company/section header.
    head_text = "\n".join(head_lines)
    doc = NLP(head_text[:1000])
    persons = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
    for p in persons:
        if _looks_like_name(p):
            return p

    # 2) Fallback: scan the first few non-empty lines for something name-shaped.
    #    Most resumes put the candidate's name on line 1-3, before any contact info.
    for line in head_lines[:6]:
        if _looks_like_name(line):
            return line

    # 3) Last resort: return the first (unvalidated) spaCy PERSON hit, if any.
    if persons:
        return persons[0]
    return None

def extract_orgs_spacy(text):
    """Organisations / institutions only, after filtering spaCy's noisy ORG tags
    (tech skills, URLs, section headers) -- see extract_resume_entities()."""
    ents = extract_resume_entities(text)
    return sorted({e["entity"] for e in ents if e["label"] in ("ORGANIZATION", "INSTITUTION")})

# ══════════════════════════════════════════════════════════════════════════════
# Resume-aware Named Entity Recognition
# ------------------------------------------------------------------------------
# Off-the-shelf spaCy models are trained on news text, so on resumes they tag
# skills as ORG/PERSON/GPE ("Docker" -> PERSON, "React" -> GPE), phone numbers as
# DATE, URLs as ORG, and they miss emails / degrees / job titles entirely.
# extract_resume_entities() keeps spaCy for what it is good at (PERSON, ORG,
# LOCATION, DATE) but validates every hit, drops technology terms, and adds
# high-precision rules for EMAIL, PHONE, URL, SKILL, DEGREE, INSTITUTION and
# JOB_TITLE, then re-labels everything with resume-friendly labels.
# ══════════════════════════════════════════════════════════════════════════════

_SKILL_TERMS = {s.lower() for s in SKILLS_DB} | set(SKILL_ALIASES)

# Skills that are also ordinary English words / single letters. Only trusted as a
# SKILL entity when they sit inside the resume's SKILLS section.
_AMBIGUOUS_SKILLS = {"c","r","go","rest","express","spring","render","node","orm",
                     "mcp","swift","rails","dart","api","shell","agile"}

_NOISE_WORDS = {
    "resume","cv","curriculum vitae","education","skills","skill","experience","projects",
    "project","summary","objective","profile","achievements","certifications","cgpa","gpa",
    "sgpa","percentage","present","current","contact","email","phone","linkedin","github",
    "technical skills","work experience","declaration","references","languages","tools",
    "frameworks","technologies","internship","internships",
}

_MONTHS = (r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
           r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|"
           r"Dec(?:ember)?)")
_DATE_RANGE_RE = re.compile(
    rf"(?:{_MONTHS}\.?,?\s+)?(?:19|20)\d{{2}}\s*(?:-|–|—|to)\s*"
    rf"(?:(?:{_MONTHS}\.?,?\s+)?(?:19|20)\d{{2}}|Present|Current|Ongoing|Now)"
    rf"|{_MONTHS}\.?,?\s+(?:19|20)\d{{2}}"
    rf"|(?<![\d.])(?:19|20)\d{{2}}(?![\d.])", re.I)

# Job-title vocabulary -- shared by resume JOB_TITLE detection and JD role extraction
_TITLE_NOUNS = (
    r"Engineer|Developer|Programmer|Scientist|Analyst|Researcher|Intern|Trainee|Manager|"
    r"Architect|Consultant|Designer|Administrator|Specialist|Lead|Director|Officer|"
    r"Associate|Tester|Technician|Strategist|Executive|Coordinator|Evangelist|Advocate|"
    r"Fellow|Apprentice|Head|Owner|SDE|SWE|Technologist"
)
_TITLE_RE = re.compile(
    rf"\b((?:[A-Z][\w\.\+#/&\-]*\s+){{0,4}}(?:{_TITLE_NOUNS})(?:\s+(?:I{{1,3}}|IV|V|\d))?)\b")
_TITLE_FILLER = {"a","an","the","our","new","great","passionate","motivated","talented",
                 "skilled","experienced","highly","dynamic","creative","enthusiastic",
                 "driven","strong","dedicated","smart","ambitious","proactive","exceptional",
                 "results-driven","detail-oriented","self-motivated","hands-on","we","are",
                 "is","looking","for","hiring","seeking","as","and","or","to","of","in",
                 "at","with","join","us","about","i","am","was","worked","working","the",
                 "responsibilities","role","position"}

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:linkedin\.com/in/[\w\-\.%]+|github\.com/[\w\-]+(?:/[\w\-\.]+)?|"
    r"leetcode\.com/[\w\-/]+|kaggle\.com/[\w\-]+|[\w\-]+\.(?:vercel\.app|netlify\.app|github\.io|"
    r"streamlit\.app|herokuapp\.com|onrender\.com))", re.I)
_PHONE_RE = re.compile(r"(?<![\w.])(?:\+?\d{1,3}[\s\-.]?)?(?:\(?\d{2,5}\)?[\s\-.]?)?\d{3,5}[\s\-.]?\d{4,5}(?![\w.])")
_INSTITUTION_KW = re.compile(r"\b(college|university|institute|school|academy|polytechnic|iit|nit|iiit|iisc)\b", re.I)
_INSTITUTION_RE = re.compile(
    r"[A-Z][\w\.&'’\-]*(?:[ \t]+(?:of|for|and|&|the|[A-Z][\w\.&'’\-]*))*?[ \t]+"
    r"(?:College|University|Institute|School|Academy|Polytechnic)"
    r"(?:[ \t]+(?:of|for|and|&)[ \t]+[A-Z][\w&]*(?:[ \t]+(?:of|and|&|[A-Z][\w&]*)){0,3})?")
_DEGREE_ENT_RE = re.compile(
    r"(?<![A-Za-z0-9])((?:Bachelors?[ \t]+of[ \t]+[A-Z][A-Za-z&]+(?:[ \t][A-Z][A-Za-z&]+){0,2}|"
    r"Masters?[ \t]+of[ \t]+[A-Z][A-Za-z&]+(?:[ \t][A-Z][A-Za-z&]+){0,2}|"
    r"B\.?[ \t]?Tech|M\.?[ \t]?Tech|B\.E\.?|M\.E\.?|BE|B\.?Sc\.?|M\.?Sc\.?|MBA|Ph\.?D\.?|BCA|MCA|"
    r"Bachelors?|Masters?|Diploma)"
    r"(?:[ \t]+(?:in|of)[ \t]+[A-Z][A-Za-z&]+(?:[ \t][A-Z][A-Za-z&]+){0,3})?)")


def _norm_ws(t):
    return re.sub(r"\s+", " ", t).strip(" ,.;:|-–—•·\t\n")


def _is_tech_or_noise(t):
    low = t.lower()
    if low in _SKILL_TERMS or low in _NOISE_WORDS:
        return True
    # multi-word strings made entirely of tech words ("Machine Learning", "Google Cloud")
    words = re.findall(r"[a-z0-9\+#\.]+", low)
    return bool(words) and all(w in _SKILL_TERMS or w in _NOISE_WORDS for w in words)


def extract_resume_entities(text, max_chars=8000):
    """Return a de-duplicated, sorted list of {"entity","label","source"} dicts.

    Labels: PERSON, EMAIL, PHONE, URL, INSTITUTION, ORGANIZATION, LOCATION,
            DEGREE, JOB_TITLE, DATE, SKILL.
    """
    if not text:
        return []
    text = text[:max_chars]
    out, seen = [], set()

    def add(ent, label, source):
        ent = _norm_ws(ent)
        if not ent:
            return
        key = (ent.lower(), label)
        if key in seen:
            return
        seen.add(key)
        out.append({"entity": ent, "label": label, "source": source})

    lines = [l.strip() for l in text.splitlines()]
    sections = split_sections(text)

    # ── 1. rule-based, high-precision entities ───────────────────────────────
    for m in _EMAIL_RE.finditer(text):
        e = extract_email(m.group(0))
        if e: add(e, "EMAIL", "Regex")

    url_spans = []
    for m in _URL_RE.finditer(text.replace("\\", "/")):
        url_spans.append(m.group(0).lower())
        add(m.group(0).rstrip("/"), "URL", "Regex")
    # phone: only from the header/contact area and only if it has 10+ digits
    head = "\n".join(lines[:15])
    for m in _PHONE_RE.finditer(head):
        cand = m.group(0).strip()
        if len(re.sub(r"\D", "", cand)) >= 10 and not _EMAIL_RE.search(cand):
            add(cand, "PHONE", "Regex"); break

    inst_spans = []
    for line in lines:
        for m in _INSTITUTION_RE.finditer(line):
            inst_spans.append(m.group(0).lower())
            add(m.group(0), "INSTITUTION", "Regex")
        for m in _DEGREE_ENT_RE.finditer(line):
            add(m.group(1), "DEGREE", "Regex")
        if len(line.split()) <= 14:
            for m in _TITLE_RE.finditer(line):
                words = m.group(1).split()
                while words and words[0].lower() in _TITLE_FILLER:
                    words.pop(0)
                if words and not _is_tech_or_noise(" ".join(words)) and len(words) <= 5:
                    add(" ".join(words), "JOB_TITLE", "Regex")

    date_spans = []
    for m in _DATE_RANGE_RE.finditer(text):
        s = _norm_ws(m.group(0))
        # skip years that belong to a longer date range already captured / phone digits
        date_spans.append(s.lower())
        add(s, "DATE", "Regex")

    skills_sec = (sections.get("skills") or "").lower()
    for skill in sorted(extract_skills(text)):
        if skill in _AMBIGUOUS_SKILLS and not re.search(
                r"(?<![a-z0-9_\-])" + re.escape(skill) + r"(?![a-z0-9_\-])", skills_sec):
            continue
        add(skill, "SKILL", "Vocabulary")

    # ── 2. spaCy, validated and re-labelled ──────────────────────────────────
    doc = NLP(text)
    for ent in doc.ents:
        t = _norm_ws(ent.text)
        low = t.lower()
        if len(t) < 2 or _is_tech_or_noise(t) or "@" in t or re.search(r"https?:|www\.|\.com|\.io", low):
            continue
        if ent.label_ == "PERSON":
            if _looks_like_name(t) and not any(w in _SKILL_TERMS or w in _NOISE_WORDS
                                               for w in low.split()):
                add(t, "PERSON", "spaCy")
        elif ent.label_ == "ORG":
            if any(low in s or s in low for s in inst_spans):
                continue                           # already captured as INSTITUTION
            if re.fullmatch(r"[\d\W]+", t) or len(t.split()) > 6:
                continue
            if _INSTITUTION_KW.search(t):
                add(t, "INSTITUTION", "spaCy")
            elif t[0].isupper() and not t.isupper() or len(t) > 4:
                add(t, "ORGANIZATION", "spaCy")
        elif ent.label_ in ("GPE", "LOC", "FAC"):
            if any(low in s for s in inst_spans) or re.search(r"\d", t):
                continue
            if t[0].isupper():
                add(t, "LOCATION", "spaCy")
        elif ent.label_ == "DATE":
            if any(low in d or d in low for d in date_spans):
                continue
            if re.search(r"(?:19|20)\d{2}", t) and len(re.sub(r"\D", "", t)) < 9:
                add(t, "DATE", "spaCy")
        # everything else (CARDINAL, PRODUCT, WORK_OF_ART, NORP, ...) is noise on resumes

    order = {"PERSON":0,"EMAIL":1,"PHONE":2,"URL":3,"INSTITUTION":4,"ORGANIZATION":5,
             "LOCATION":6,"DEGREE":7,"JOB_TITLE":8,"DATE":9,"SKILL":10}
    out.sort(key=lambda d: (order.get(d["label"], 99), d["entity"].lower()))
    return out


# ══════════════════════════════════════════════════════════════════════════════
# Job role extraction from a Job Description
# ══════════════════════════════════════════════════════════════════════════════

_JD_LABEL_RE = re.compile(
    r"(?i)^\W*(?:job\s*title|job\s*role|role|position|designation|title|opening|vacancy|"
    r"hiring\s*for|post|profile)\s*[:\-–—]\s*(.+)$")
_JD_PHRASE_RE = re.compile(
    rf"(?i)(?:looking\s+for|seeking|hiring|searching\s+for|opening\s+for|applications?\s+for|"
    rf"role\s+of|position\s+of|join\s+(?:us|our\s+team)\s+as|apply\s+for|recruiting)\s+"
    rf"(?:an?\s+|the\s+)?((?:[\w\.+#/&\-]+\s+){{0,5}}?(?:{_TITLE_NOUNS}))\b")
_JD_SPLIT_RE = re.compile(r"\s+[-–—|@]\s+|\s*[|•·]\s*|\s+at\s+|\s+in\s+|\s*\(|\s*,\s*|\s*/\s*(?=[A-Z])|\s+for\s+")


def _clean_role(raw):
    r = re.sub(r"(?i)\b(job\s*description|job\s*title|jd)\b\s*[:\-–—]?", "", raw)
    r = _JD_SPLIT_RE.split(r.strip())[0]
    r = _norm_ws(r)
    words = r.split()
    while words and words[0].lower() in _TITLE_FILLER:
        words.pop(0)
    r = " ".join(words)
    if r.isupper() or r.islower():
        r = r.title()
    return r[:60] if 2 <= len(r) else None


def extract_job_role(jd_text):
    """Best-effort job role/title from a job description; None if not detectable.

    Strategy (first hit wins): labelled field ("Job Title: ...") -> heading line
    that looks like a title -> "we are looking for a ..." phrase -> most frequent
    title-like phrase in the opening of the JD.
    """
    if not jd_text or not jd_text.strip():
        return None
    lines = [l.strip() for l in jd_text.splitlines() if l.strip()]

    # 1) labelled field
    for l in lines[:40]:
        m = _JD_LABEL_RE.match(l)
        if m:
            r = _clean_role(m.group(1))
            if r and _TITLE_RE.search(r):
                return r

    # 2) a short heading line near the top that is itself a title
    for l in lines[:6]:
        if len(l.split()) <= 10 and not l.endswith("."):
            m = _TITLE_RE.search(_clean_role(l) or "")
            if m:
                r = _clean_role(m.group(1))
                if r and not _is_tech_or_noise(r):
                    return r

    # 3) natural-language phrase
    m = _JD_PHRASE_RE.search(jd_text[:3000])
    if m:
        r = _clean_role(m.group(1))
        if r and not _is_tech_or_noise(r):
            return r

    # 4) most frequent title-like phrase in the opening of the JD
    counts = {}
    for m in _TITLE_RE.finditer(jd_text[:1500]):
        words = m.group(1).split()
        while words and words[0].lower() in _TITLE_FILLER:
            words.pop(0)
        cand = " ".join(words)
        if cand and not _is_tech_or_noise(cand):
            counts[cand] = counts.get(cand, 0) + 1
    if counts:
        return max(counts, key=lambda k: (counts[k], len(k)))
    return None

# ── section splitting ────────────────────────────────────────────────────────

SECTION_HEADERS = {
    "summary":        r"(?i)^\s*(summary|objective|profile|about\s*me|introduction|overview)\s*$",
    "education":      r"(?i)^\s*(education|academic|qualification|degree|schooling)\s*$",
    "experience":     r"(?i)^\s*(experience|employment|work\s*history|career|internship|positions?|roles?|professional\s*background)\s*$",
    "skills":         r"(?i)^\s*(skills?|technical\s*skills?|competencies|technologies|tools|languages|frameworks?|core\s*skills?)\s*$",
    "projects":       r"(?i)^\s*(projects?|project\s*work|portfolio|side\s*projects?|personal\s*projects?|academic\s*projects?|key\s*projects?|notable\s*projects?|selected\s*projects?)\s*$",
    "certifications": r"(?i)^\s*(certif\w*(\s*(&|and)\s*accomplishments)?|licenses?|credentials?|courses?|training)\s*$",
    "achievements":   r"(?i)^\s*(achievements?|awards?|honours?|honors?|accomplishments?|academic\s*and\s*extracurricular\s*achievements?)\s*$",
    "other_headers":  r"(?i)^\s*(extra[\s\-]*curricul\w*(\s*(&|and)?\s*(activities|leadership))?|activities|leadership|languages?\s*known|language\s*proficiency|interests?|hobbies)\s*$",
}

# Strip leading emoji/bullets/numbering and trailing colons/dashes so headers like
# "🚀 Projects:" or "2. TECHNICAL SKILLS -" still match the plain-word patterns below.
_HEADER_STRIP_RE = re.compile(
    r"^[\W_]*\d*[\.\)]?\s*|[\s:\-–—]+$", re.UNICODE)

def _clean_header_line(line):
    cleaned = _HEADER_STRIP_RE.sub("", line)
    return cleaned.strip()

def split_sections(text):
    lines = text.splitlines()
    sections = {k: [] for k in SECTION_HEADERS}
    sections["other"] = []
    current = "other"
    for line in lines:
        matched = False
        stripped = line.strip()
        if stripped and len(stripped) < 60:
            candidate = _clean_header_line(stripped)
            if candidate:
                for sec, pattern in SECTION_HEADERS.items():
                    if re.search(pattern, candidate):
                        current = sec; matched = True; break
        if not matched:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}

# ── field extractors ─────────────────────────────────────────────────────────

DEGREE_RE = re.compile(
    r"(?<![A-Za-z0-9\.])"
    r"(B\.?Tech|B\.?E\.?|B\.?Sc?\.?|M\.?Tech|M\.?Sc?\.?|MBA|Ph\.?D\.?|"
    r"Bachelor|Master|Doctorate|Associate|Diploma|B\.?A\.?|M\.?A\.?|BCA|MCA)"
    r"[^\n]{0,80}", re.I)
YEAR_RE = re.compile(r"\b((19|20)\d{2})\b")

def extract_skills(text):
    text_lower = text.lower()
    found = set()
    for skill in SKILLS_DB:
        pat = r"(?<![a-zA-Z0-9_\-])" + re.escape(skill) + r"(?![a-zA-Z0-9_\-])"
        if re.search(pat, text_lower): found.add(skill)
    for alias, canonical in SKILL_ALIASES.items():
        pat = r"(?<![a-zA-Z0-9_\-])" + re.escape(alias) + r"(?![a-zA-Z0-9_\-])"
        if re.search(pat, text_lower): found.add(canonical)
    return sorted(found)

def canonicalize_skill(term):
    """Resolve a raw skill string to its canonical SKILLS_DB form via SKILL_ALIASES,
    so a ground-truth entry like "cpp" or "ReactJS" matches an extracted "c++" or
    "react" instead of being scored as a miss just because of wording."""
    t = re.sub(r"\s+", " ", str(term).strip().lower())
    return SKILL_ALIASES.get(t, t)

def extract_education(text):
    entries = []
    for m in DEGREE_RE.finditer(text):
        entry = m.group(0).strip()
        years = [y[0] for y in YEAR_RE.findall(entry)]
        entries.append({"degree": entry, "years": years})
    return entries

def extract_experience(text):
    date_re = re.compile(
        r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?|Present|Current)[,\s]*(\d{4})?", re.I)
    entries = []
    for block in re.split(r"\n{2,}", text):
        block = block.strip()
        if not block: continue
        years  = [y[0] for y in YEAR_RE.findall(block)]
        dates  = [" ".join(d).strip() for d in date_re.findall(block)]
        entries.append({"description": block[:300], "years": years, "dates_mentioned": dates})
    return entries[:10]

# Action verbs that signal a real project description
_ACTION_RE = re.compile(
    r"\b(built|developed|created|designed|implemented|deployed|integrated|"
    r"engineered|architected|automated|optimized|improved|reduced|increased|"
    r"led|managed|researched|analyzed|trained|fine.tuned|scraped|parsed|"
    r"extracted|visualized|published|launched|delivered|produced|generated|"
    r"trained|evaluated|benchmarked|contributed|collaborated|maintained)\b", re.I)

# Patterns that indicate a line is a skills list, NOT a project
_SKILLS_LIST_RE = re.compile(
    r"^[\w\s\.\+\#\/\-\,\|&]+$")   # only alphanum + punctuation, no sentence structure

_BULLET_RE = re.compile(r"^\s*[•\-\*▸→‣●○–—]\s*")
# A self-contained "Title: description" or "Title | description" bullet, where one
# whole bullet line IS one project (common in dense one-bullet-per-project resumes).
_TITLE_HEAD_RE = re.compile(r"^([A-Z][^:|–—\n]{1,60}?)[:|–—]\s+(.+)$")
_TITLE_HEAD_BLACKLIST = {
    "tech","technologies","tools","stack","tech stack","technology",
    "technology used","skills","impact","note","result","results","outcome",
}
# A short "Project Title | Tech, Stack" style line (used as a fallback signal elsewhere).
_PROJECT_TITLE_RE = re.compile(r"^[A-Z][\w \-/&\.]{1,60}\s*[\|:–—-]\s*.{3,}")
# Inline heading anywhere in the raw resume, e.g. "Projects: Built an X that does Y"
_PROJECT_INLINE_RE = re.compile(
    r"(?im)^\s*(?:projects?|academic\s*projects?|personal\s*projects?)\s*[:\-]\s*(.+)$")

def _is_project_title_head(head):
    h = head.strip().lower()
    if h in _TITLE_HEAD_BLACKLIST:
        return False
    if _ACTION_RE.match(head.strip()):
        return False
    if _is_prose_line(head.strip()):
        return False
    return True

def _is_prose_line(line):
    """A line is 'prose' (i.e. a wrapped sentence fragment, not a project title)
    if it starts lowercase (real titles are always capitalized) or if a large
    fraction of its words are ordinary lowercase words."""
    if not line:
        return False
    if line[0].islower():
        return True
    words = re.findall(r"[A-Za-z][A-Za-z\-']*", line)
    if len(words) < 4:
        return False
    lowercase_words = [w for w in words if w.islower() and len(w) > 1]
    return (len(lowercase_words) / len(words)) > 0.35

def _split_project_blocks(text):
    """Split a projects-section string into candidate project blocks.
    Tries blank-line paragraphs first; if the section is one dense wall of
    bullet points (no blank lines — very common), use bullet/title heuristics
    that distinguish: a new project title, a self-contained one-line bullet
    project, a description bullet belonging to the current project, and a
    wrapped continuation line of the previous bullet."""
    blocks = [b for b in re.split(r"\n{2,}", text) if b.strip()]
    if len(blocks) > 1:
        return blocks

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return blocks

    n = len(lines)
    new_blocks, current = [], []
    for i, raw_line in enumerate(lines):
        has_bullet = bool(_BULLET_RE.match(raw_line))
        line = _BULLET_RE.sub("", raw_line).strip()
        next_has_bullet = (i + 1 < n) and bool(_BULLET_RE.match(lines[i + 1]))

        m = _TITLE_HEAD_RE.match(line)
        self_contained_title = bool(m) and _is_project_title_head(m.group(1))
        # A non-bulleted line immediately followed by a bullet is a heading —
        # unless it reads like a wrapped sentence (mostly lowercase words),
        # in which case it's a continuation of the previous bullet.
        heading_line = (not has_bullet) and next_has_bullet and not _is_prose_line(line.split(".")[0])

        starts_new = self_contained_title or heading_line or not current
        if starts_new:
            if current:
                new_blocks.append(" ".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        new_blocks.append(" ".join(current))
    return new_blocks if len(new_blocks) > 1 else blocks

def extract_projects(text, full_text=""):
    entries = []
    seen = set()

    def _add(block):
        block = block.strip().lstrip("•-*→▸●○ ")
        if len(block) < 25:
            return
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            return
        full = " ".join(lines)
        key = full[:60].lower()
        if key in seen:
            return
        # Reject if it's a comma/pipe-separated tech list (no sentence verbs)
        if _SKILLS_LIST_RE.match(full) and not _ACTION_RE.search(full):
            return
        # Short bullet-style entries are fine as long as they have an action verb
        # or look like a "Title | description" line; otherwise require more length.
        if len(full) < 40 and not (_ACTION_RE.search(full) or _PROJECT_TITLE_RE.match(full)):
            return
        seen.add(key)
        entries.append(block[:400])

    if text.strip():
        for block in _split_project_blocks(text):
            _add(block)

    # Fallback: section-header detection may have missed an inline "Projects:" line
    # (heading and content on the same line). Scan the full raw text for that pattern.
    if not entries and full_text.strip():
        for m in _PROJECT_INLINE_RE.finditer(full_text):
            _add(m.group(1))

    return entries[:12]

def _extract_bullet_lines(text):
    entries = []
    for line in text.splitlines():
        line = line.strip().lstrip("•-* ")
        if len(line) >= 6:
            entries.append(line)
    return entries[:20]

def extract_certifications(text):
    return _extract_bullet_lines(text)

def extract_achievements(text):
    return _extract_bullet_lines(text)

# ── main ─────────────────────────────────────────────────────────────────────

def parse_resume(file_path):
    raw_text  = extract_text(file_path)
    # Pull hyperlinks that may not appear as plain text (clickable icons in PDFs/DOCX)
    hyperlinks = get_extra_urls(file_path)
    # Append hyperlink URLs to the search corpus for contact field extraction
    contact_corpus = raw_text + "\n" + "\n".join(hyperlinks)

    sections  = split_sections(raw_text)
    return {
        "raw_text":       raw_text,
        "name":           extract_name_spacy(raw_text),
        "email":          extract_email(contact_corpus),
        "phone":          extract_phone(contact_corpus),
        "linkedin":       extract_linkedin(contact_corpus),
        "github":         extract_github(contact_corpus),
        "skills":         extract_skills(raw_text),
        "education":      extract_education(sections.get("education","") or raw_text),
        "experience":     extract_experience(sections.get("experience","") or ""),
        "projects":       extract_projects(sections.get("projects","") or "", raw_text),
        "certifications": extract_certifications(sections.get("certifications","") or ""),
        "achievements":    extract_achievements(sections.get("achievements","") or ""),
        "summary":        sections.get("summary",""),
        "organisations":  extract_orgs_spacy(raw_text),
    }
