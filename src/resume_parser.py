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
    from src.structure import pdf_text
    try:
        return pdf_text(path)
    except Exception:
        text = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t: text.append(t)
        return "\n".join(text)

def extract_text_from_docx(path):
    from src.structure import docx_text
    try:
        return docx_text(path)
    except Exception:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

def extract_text(path):
    from src.structure import prepare_text
    ext = Path(path).suffix.lower()
    if ext == ".pdf":   raw = extract_text_from_pdf(path)
    elif ext in (".docx",".doc"): raw = extract_text_from_docx(path)
    else:
        with open(path,"r",errors="ignore") as f: raw = f.read()
    return prepare_text(raw)

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
    for m in re.finditer(r"(?<![\w.])\+?\(?\d[\d \t\-.()]{8,17}\d(?![\w.])", text):
        cand = m.group(0).strip()
        if len(re.sub(r"\D", "", cand)) > 14:
            cand = re.sub(r"^\d{5,6}\s+", "", cand)
        if 10 <= len(re.sub(r"\D", "", cand)) <= 14:
            return cand
    return None

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

# Everything except EMAIL, PHONE and DATE is detected by GLiNER now. These are
# the exact label strings GLiNER is prompted with -- it's a zero-shot model, so
# it isn't limited to a fixed training-set vocabulary the way spaCy's tagger is,
# and prompting it with the specific label we want (e.g. "job title" instead of
# spaCy's generic news-domain categories) is what makes it noticeably better at
# resume-style PERSON / ORGANIZATION / LOCATION / INSTITUTION / DEGREE /
# JOB_TITLE / URL extraction.
_GLINER_LABELS = ["person", "organization", "location", "institution",
                   "degree", "job title", "url"]
_GLINER_LABEL_MAP = {
    "person": "PERSON", "organization": "ORGANIZATION", "location": "LOCATION",
    "institution": "INSTITUTION", "degree": "DEGREE", "job title": "JOB_TITLE",
    "url": "URL",
}
_GLINER_MODEL = None
_GLINER_UNAVAILABLE = False   # set once if loading fails, so we don't retry every call


def _get_gliner():
    """Lazily load GLiNER (zero-shot NER) once per process. Returns None if the
    package isn't installed or the model can't be downloaded/found locally, so
    callers can fall back to the regex rules instead of crashing."""
    global _GLINER_MODEL, _GLINER_UNAVAILABLE
    if _GLINER_MODEL is not None or _GLINER_UNAVAILABLE:
        return _GLINER_MODEL
    try:
        from gliner import GLiNER
        _GLINER_MODEL = GLiNER.from_pretrained("urchade/gliner_small-v2.1")
    except Exception:
        _GLINER_UNAVAILABLE = True
        _GLINER_MODEL = None
    return _GLINER_MODEL


def _gliner_entities(text, labels=None):
    """Run GLiNER over `text` for the given zero-shot labels (default: every
    label in _GLINER_LABELS). Returns a list of {"text","label"} with `label`
    already mapped to our canonical names (PERSON, ORGANIZATION, ...), or None
    if GLiNER isn't available -- callers fall back to the regex rules in that
    case, which is the only situation those rules still run in."""
    model = _get_gliner()
    if model is None:
        return None
    labels = labels or _GLINER_LABELS
    try:
        preds = model.predict_entities(text, labels, threshold=0.5)
        return [{"text": p["text"], "label": _GLINER_LABEL_MAP.get(p["label"], p["label"])}
                for p in preds]
    except Exception:
        return None


def _person_org_loc_entities(text, doc=None):
    """PERSON / ORGANIZATION / LOCATION candidates for `text`, as a list of
    {"text", "label"} with label in {"person","organization","location"}
    (lower-case, pre-mapping -- kept for extract_name_spacy's simpler needs).
    Falls back to spaCy's `doc` (already NLP(text)) if GLiNER is unavailable.
    """
    preds = _gliner_entities(text, labels=["person", "organization", "location"])
    if preds is not None:
        inv = {"PERSON": "person", "ORGANIZATION": "organization", "LOCATION": "location"}
        return [{"text": p["text"], "label": inv.get(p["label"], p["label"].lower())} for p in preds]
    out = []
    if doc is not None:
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                out.append({"text": ent.text, "label": "person"})
            elif ent.label_ == "ORG":
                out.append({"text": ent.text, "label": "organization"})
            elif ent.label_ in ("GPE", "LOC", "FAC"):
                out.append({"text": ent.text, "label": "location"})
    return out


def _repair_name_line(line):
    """Fix names broken by small-caps or letter-spaced styling:
    'A MANs harma' -> 'Aman Sharma', 'A I DEN Williams' -> 'Aiden Williams'."""
    toks = line.split()
    if not (2 <= len(toks) <= 8) or re.search(r"[\d@/|,:]", line):
        return line
    odd = any(len(t) == 1 and t.isupper() for t in toks) or any(
        re.search(r"[A-Z]{2,}[a-z]", t) for t in toks)
    if not odd or not all(t.isalpha() for t in toks):
        return line
    if not any(re.search(r"[a-z]", t) for t in toks):
        return line                             # all caps: initials like 'K R SAI SHARAN' are real
    if sum(bool(re.fullmatch(r"[A-Z][a-z]{2,}", t)) for t in toks) >= 2:
        return line                             # already fine ('Sai Sharan K R')
    expanded = []
    for t in toks:                              # 'MANs' -> 'MAN', 's' (small-caps: lowercase starts a new word)
        m = re.fullmatch(r"([A-Z]{2,})([a-z]+)", t)
        expanded.extend([m.group(1), m.group(2)] if m else [t])
    words, buf = [], ""
    for t in expanded:
        if re.fullmatch(r"[A-Z][a-z]{2,}", t):          # a normal Titlecase word ends the fragment run
            if buf: words.append(buf); buf = ""
            words.append(t)
        elif t.isupper():
            buf += t
            if len(t) >= 3:
                words.append(buf); buf = ""
        else:                                            # lowercase fragment(s)
            buf += t
    if buf:
        words.append(buf)
    if not 2 <= len(words) <= 4:
        return line
    return " ".join(w.capitalize() if not re.fullmatch(r"[A-Z][a-z]+", w) else w for w in words)


def _name_from_email(name, email):
    """Re-split a name whose word breaks were misread, using the email as a witness:
    'Amans Harm A' + asharmaal@... -> 'Aman Sharma' (the surname 'sharma' is in the email)."""
    if not name or not email:
        return name
    local = re.sub(r"[^a-z]", "", email.split("@")[0].lower())
    toks = name.split()
    letters = re.sub(r"[^a-z]", "", name.lower())
    if len(letters) < 6 or len(local) < 4:
        return name
    last = re.sub(r"[^a-z]", "", toks[-1].lower())
    if len(last) >= 4 and last in local:
        return name                                   # already consistent with the email
    for n in range(len(letters) - 2, 3, -1):          # longest surname first
        sur = letters[-n:]
        if sur in local and len(letters) - n >= 2:
            first = letters[:-n]
            return f"{first.capitalize()} {sur.capitalize()}"
    return name


def extract_name_spacy(text):
    """Name extraction is layout-first, spaCy-second.

    spaCy's PERSON tag is trained on news text, so on a resume header line like
    "SAI SHARAN  |  Bengaluru  |  sai@gmail.com" it regularly mis-tags, misses the
    name entirely, or grabs a trailing word. But a resume's name is almost always
    the very first non-empty line, in Title Case or ALL CAPS, with no digits,
    email, or contact symbols -- a far more reliable signal than generic NER here.
    So the layout heuristic goes first; spaCy is only a fallback for odd layouts
    (e.g. a logo/line above the name, or the name on line 2-3).
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    head_lines = lines[:15]

    # 1) Layout heuristic: the first candidate-shaped line in the header, also
    #    handling an ALL CAPS name (common in resume templates) by title-casing
    #    it before validation.
    for line in head_lines[:5]:
        candidate = _repair_name_line(line)
        if candidate.isupper():
            candidate = candidate.title()
        if _looks_like_name(candidate):
            return candidate

    # 2) GLiNER (falling back to spaCy) PERSON entities near the top, validated
    #    the same way.
    head_text = "\n".join(head_lines)
    doc = NLP(head_text[:1000])
    ents = _person_org_loc_entities(head_text[:1000], doc)
    persons = [e["text"].strip() for e in ents if e["label"] == "person"]
    for p in persons:
        if _looks_like_name(p):
            return p

    # 3) Looser layout scan further down the header.
    for line in head_lines[5:8]:
        if _looks_like_name(line):
            return line

    # 4) Last resort: first (unvalidated) spaCy PERSON hit, if any.
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

# Job-title vocabulary -- shared by resume JOB_TITLE detection and JD role extraction.
# Includes internship/co-op/graduate-program nouns since those are job *roles* on
# JDs just as much as full-time titles, and ATS systems extract them the same way.
_TITLE_NOUNS = (
    r"Engineer|Developer|Programmer|Scientist|Analyst|Researcher|Intern|Internship|"
    r"Trainee|Traineeship|Manager|Architect|Consultant|Designer|Administrator|"
    r"Specialist|Lead|Director|Officer|Associate|Tester|Technician|Strategist|"
    r"Executive|Coordinator|Evangelist|Advocate|Fellow|Apprentice|Apprenticeship|"
    r"Head|Owner|SDE|SWE|Technologist|Co-?op"
)
# Case-insensitive, plural-tolerant version for matching inside free-flowing JD
# prose ("hiring software engineers", "seeking data science interns").
_TITLE_NOUNS_PLURAL = rf"(?:{_TITLE_NOUNS})s?"
_TITLE_RE = re.compile(
    rf"\b((?:[A-Z][\w\.\+#/&\-]*\s+){{0,4}}(?:{_TITLE_NOUNS})(?:\s+(?:I{{1,3}}|IV|V|\d))?)\b")
# Looser variant used only for JD text: allows lowercase words and plurals, since
# JD prose is often not capitalized the way a resume heading or title line is.
# Word separators are [ \t] rather than \s so a match can never cross a newline
# (which would otherwise bleed one line's trailing word into the next line's
# title), and the prefix charclass excludes "." so a sentence-ending period
# doesn't get swallowed as part of a "word".
_TITLE_RE_LOOSE = re.compile(
    rf"(?i)\b((?:[\w\+#/&\-]+[ \t]+){{0,4}}{_TITLE_NOUNS_PLURAL}(?:[ \t]+(?:I{{1,3}}|IV|V|\d))?)\b")
_TITLE_FILLER = {"a","an","the","our","new","great","passionate","motivated","talented",
                 "skilled","experienced","highly","dynamic","creative","enthusiastic",
                 "driven","strong","dedicated","smart","ambitious","proactive","exceptional",
                 "results-driven","detail-oriented","self-motivated","hands-on","we","are",
                 "is","looking","for","hiring","seeking","as","and","or","to","of","in",
                 "at","with","join","us","about","i","am","was","worked","working","the",
                 "responsibilities","role","position","urgent","urgently","requirement",
                 "requirements","need","needed","immediate","opening","openings","vacancy",
                 "vacancies","post","profile","applications","invited","now","currently",
                 "recruiting","apply","application","wanted","required","require"}

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:linkedin\.com/in/[\w\-\.%]+|github\.com/[\w\-]+(?:/[\w\-\.]+)?|"
    r"leetcode\.com/[\w\-/]+|kaggle\.com/[\w\-]+|[\w\-]+\.(?:vercel\.app|netlify\.app|github\.io|"
    r"streamlit\.app|herokuapp\.com|onrender\.com))", re.I)
_PHONE_RE = re.compile(r"(?<![\w.])\+?\(?\d[\d \t\-.()]{8,17}\d(?![\w.])")
# Company suffixes / patterns -- catches employer names spaCy's generic ORG tag
# regularly misses or mis-boundaries on resumes ("Infosys Pvt. Ltd.", "Acme Technologies").
_ORG_SUFFIX_RE = re.compile(
    r"\b([A-Z][\w&'\.\-]*(?:[ \t]+[A-Z][\w&'\.\-]*){0,4}[ \t]+"
    r"(?:Pvt\.?[ \t]?Ltd\.?|Private[ \t]Limited|Ltd\.?|LLC|LLP|Inc\.?|Corp\.?|"
    r"Corporation|Technologies|Technology|Solutions|Systems|Labs|Laboratories|"
    r"Consulting|Industries|Enterprises|Group|Ventures|Software|Networks|"
    r"Analytics|Innovations|Infotech|Softwares|Pvt))\b")
# "<Role> at <Company>" / "<Role> with <Company>" lines under an Experience or
# Internship section header -- the layout ATS parsers lean on most. Deliberately
# requires the literal "at"/"with" keyword (not just "line starts with a capital
# letter"): without that anchor there's no reliable way to tell a title-first
# line ("Software Engineering Intern, Acme Technologies") from a company-first
# one ("Infosys, Machine Learning Intern") by punctuation alone, and guessing
# wrong pollutes the organisation list with job titles. No (?i) here on purpose
# -- it's the capitalisation of the company name itself that makes this safe.
_EXPERIENCE_HEADERS = re.compile(
    r"(?i)^\s*(work\s+experience|experience|professional\s+experience|employment\s+history|"
    r"internships?|career\s+history)\s*:?\s*$")
_EXP_LINE_ORG_RE = re.compile(
    r"\b(?:at|with)\s+([A-Z][\w&'\.\-]*(?:[ \t]+(?:of|and|&|[A-Z][\w&'\.\-]*)){0,4})"
    r"\s*(?:[,\|\u2013\u2014\-]|\s+\(|$)")
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


_GENERIC_TAIL = {"modules","management","efficiency","operations","control","analysis","development",
                 "design","leadership","skills","accuracy","collaboration","planning","strategy",
                 "training","testing","reporting","service","services","systems","virtualization",
                 "gauge","handle","game","widget","system","platform","engineering","science"}


_STRONG_ORG = re.compile(
    r"(?i)\b(inc|llc|ltd|limited|pvt|private|corp|corporation|company|co|clinic|hospital|bank|foundation|"
    r"association|society|council|agency|group|health|healthcare|enterprises|ventures|labs|solutions|"
    r"technologies|consulting|consultants|services|industries|partners|capital|studios?|airlines|motors)\b")


def _merge_structure(text, out):
    """Use the parsed structure (companies, institutions, titles, locations, dates)
    to validate what the model/regex found and to fill in what it missed."""
    from src import structure as st
    try:
        a = analyse_structure(text)
    except Exception:
        return out
    exp, edu = a["experience"], a["education"]
    s_comp = [st.clean_org(e.get("company")) for e in exp if isinstance(e, dict) and e.get("company")]
    s_inst = [e["institution"] for e in edu if isinstance(e, dict) and e.get("institution")]
    s_issuer = st.issuer_orgs(a["certifications"])
    s_title = [e["title"] for e in exp if isinstance(e, dict) and e.get("title")]
    s_deg = [e["degree"] for e in edu if isinstance(e, dict) and e.get("degree")]
    s_loc = [x for x in ([a["location"]] + [e.get("location") for e in exp + edu if isinstance(e, dict)]) if x]
    s_dates = [e["dates"] for e in exp + edu if isinstance(e, dict) and e.get("dates")]
    for it in a["projects"]:
        m = re.search(r"\(([^()]*(?:19|20)\d{2}[^()]*)\)", it)
        if m and st.DATE_RANGE.search(m.group(1)) or (m and st.DATE_SINGLE.search(m.group(1))):
            s_dates.append(m.group(1))

    low = lambda x: x.lower()
    known_org = {low(x) for x in s_comp + s_issuer}
    known_inst = {low(x) for x in s_inst}
    have_struct = bool(known_org or known_inst)
    skills_sec = (a["sections"].get("skills") or "").lower()
    head_line = (a["headline"] or "").lower()
    listed_low = {x.lower() for x in a["listed_skills"]}
    loc_parts = {p.strip().lower() for l in s_loc for p in re.split(r",\s*", l) if p.strip()}
    loc_parts |= {re.sub(r"\d+", "", p).strip() for p in list(loc_parts)}
    cities = {p.split(",")[0].strip().lower() for p in s_loc}

    def ok_org(e):
        t, lw = e["entity"], e["entity"].lower()
        if lw in known_org or lw in known_inst:
            return True
        if "," in t or re.search(r"\d", t) or len(t.split()) > 6:
            return False
        if re.match(r"^[A-Z]{2}\s", t) and t.split()[0] in st._US_ABBR:
            return False
        if lw in listed_low or lw in head_line or (skills_sec and lw in skills_sec):
            return False
        if any(lw in x.lower() for x in a["achievements"]):
            return False
        if st.has_title_word(t) and not st._ORG_SUFFIX.search(t):
            return False
        if t.split()[-1].lower() in _GENERIC_TAIL and not st._ORG_SUFFIX.search(t):
            return False
        if t.lower() in {d.lower() for d in s_deg} or st._DEGREE_LINE.search(t) and not st._INST_RE.search(t):
            return False
        if have_struct and not _STRONG_ORG.search(t):
            return False
        return True

    kept = []
    for e in out:
        lab, t = e["label"], e["entity"]
        if e["source"] == "Structure":
            kept.append(e); continue
        if lab == "ORGANIZATION" and not ok_org(e):
            continue
        if lab == "INSTITUTION":
            if "," in t or t.lower() in st._GENERIC_EDU or (not st._INST_RE.search(t) and low(t) not in known_inst):
                continue
        if lab == "PERSON" and a["name"] and not (t.lower() == a["name"].lower() or t.lower() in a["name"].lower()):
            continue
        if lab == "LOCATION":
            lw = t.lower()
            if re.search(r"\d", t) or st.has_title_word(t) or lw in listed_low:
                continue
            _W = st._load_words()
            if _W.get(lw, 1e9) <= _W.get("__max__", 0) and lw not in cities and lw not in st._REGIONS and lw not in loc_parts:
                continue                        # a common English word ("Employee"), not a place
            if loc_parts and lw not in loc_parts and lw not in st._REGIONS and lw not in cities:
                continue
        if lab == "DEGREE" and (not st._DEGREE_LINE.search(t) or (len(t) < 4 and "." not in t)):
            continue
        if lab == "JOB_TITLE" and not st.has_title_word(t):
            continue
        if lab == "DATE" and not re.search(r"(?:19|20)\d{2}|present|current", t, re.I):
            continue
        kept.append(e)

    seen = {(e["entity"].lower(), e["label"]) for e in kept}
    def add(ent, label):
        ent = _norm_ws(ent)
        if not ent:
            return
        if (ent.lower(), label) in seen:
            for e in kept:
                if e["label"] == label and e["entity"].lower() == ent.lower():
                    e["source"] = "Structure"
            return
        seen.add((ent.lower(), label))
        kept.append({"entity": ent, "label": label, "source": "Structure"})
    if a["name"]: add(a["name"], "PERSON")
    for x in s_comp + s_issuer: add(x, "ORGANIZATION")
    for x in s_inst: add(x, "INSTITUTION")
    for x in s_title: add(x, "JOB_TITLE")
    for x in s_deg: add(x, "DEGREE")
    for x in s_loc: add(x, "LOCATION")
    for x in s_dates: add(x, "DATE")
    # a degree/title is never also an organisation
    drop = {low(x) for x in s_deg + s_title}
    kept = [e for e in kept if not (e["label"] in ("ORGANIZATION", "INSTITUTION", "LOCATION") and low(e["entity"]) in drop)]
    # an entity wholly contained in a longer one of the same label is a fragment
    def _frag(e, lst):
        lw = e["entity"].lower()
        return any(o is not e and o["label"] == e["label"] and lw != o["entity"].lower() and lw in o["entity"].lower()
                   and (o["source"] == "Structure" or e["label"] in ("DATE", "DEGREE", "INSTITUTION", "LOCATION"))
                   for o in lst)
    kept = [e for e in kept if not (e["label"] in ("DATE", "DEGREE", "INSTITUTION", "LOCATION") and e["source"] != "Structure" and _frag(e, kept))]
    # "CA San Diego State University" / "Present Warehouse Operations Manager": prefix noise
    def _noisy(e, lst):
        lw = e["entity"].lower()
        return e["source"] != "Structure" and any(
            o["source"] == "Structure" and o["label"] == e["label"] and o["entity"].lower() != lw and o["entity"].lower() in lw
            for o in lst)
    kept = [e for e in kept if not _noisy(e, kept)]
    # inst/org duplicates -> institution wins
    inst_l = {e["entity"].lower() for e in kept if e["label"] == "INSTITUTION"}
    kept = [e for e in kept if not (e["label"] == "ORGANIZATION" and e["entity"].lower() in inst_l)]
    return kept


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

    # phone: only from the header/contact area and only if it has 10+ digits
    head = "\n".join(lines[:15])
    for m in _PHONE_RE.finditer(head):
        cand = m.group(0).strip()
        if len(re.sub(r"\D", "", cand)) >= 10 and not _EMAIL_RE.search(cand):
            add(cand, "PHONE", "Regex"); break

    date_spans = []
    for m in _DATE_RANGE_RE.finditer(text):
        s = _norm_ws(m.group(0))
        date_spans.append(s.lower())
        add(s, "DATE", "Regex")

    skills_sec = (sections.get("skills") or "").lower()
    for skill in sorted(extract_skills(text)):
        if skill in _AMBIGUOUS_SKILLS and not re.search(
                r"(?<![a-z0-9_\-])" + re.escape(skill) + r"(?![a-z0-9_\-])", skills_sec):
            continue
        add(skill, "SKILL", "Vocabulary")

    # ── 2. Everything else: GLiNER, with the old regex rules as a fallback ────
    # Only EMAIL, PHONE and DATE stay regex-based above. PERSON, ORGANIZATION,
    # LOCATION, INSTITUTION, DEGREE, JOB_TITLE and URL are all GLiNER now -- it's
    # a zero-shot NER model prompted directly with these label names, rather
    # than spaCy's fixed news-domain categories or a hand-written pattern, which
    # is why it reads resume-style text more reliably across all of them. The
    # regex/spaCy rules below only run if GLiNER isn't installed or its weights
    # aren't available locally (first run needs internet to download them once).
    gliner_preds = _gliner_entities(text)
    doc = NLP(text)   # still needed for the DATE regex's spaCy supplement, and
                       # as the fallback source if GLiNER is unavailable
    src_label = "GLiNER" if gliner_preds is not None else "spaCy/Regex"

    if gliner_preds is not None:
        inst_spans, org_spans = [], []

        def clean(t):
            t = _norm_ws(t)
            if t.isupper() or t.islower():
                t = t.title()
            return t

        # institutions first, so organisation/location can be checked against them
        for e in gliner_preds:
            if e["label"] != "INSTITUTION":
                continue
            t = clean(e["text"])
            if len(t) < 2 or _is_tech_or_noise(t):
                continue
            inst_spans.append(t.lower())
            add(t, "INSTITUTION", src_label)

        for e in gliner_preds:
            t_raw = _norm_ws(e["text"])
            low = t_raw.lower()
            if len(t_raw) < 2 or _is_tech_or_noise(t_raw):
                continue
            label = e["label"]
            if label == "INSTITUTION":
                continue   # already handled above
            if label == "DEGREE":
                add(t_raw, "DEGREE", src_label)
            elif label == "URL":
                add(t_raw.rstrip("/"), "URL", src_label)
            elif label == "JOB_TITLE":
                words = t_raw.split()
                while words and words[0].lower() in _TITLE_FILLER:
                    words.pop(0)
                if words and not _is_tech_or_noise(" ".join(words)):
                    add(" ".join(words), "JOB_TITLE", src_label)
            elif label == "PERSON":
                t = clean(t_raw)
                if "@" in t_raw or re.search(r"https?:|www\.|\.com|\.io", low):
                    continue
                if _looks_like_name(t) and not any(w in _SKILL_TERMS or w in _NOISE_WORDS
                                                    for w in low.split()):
                    add(t, "PERSON", src_label)
            elif label == "ORGANIZATION":
                if "@" in t_raw or re.search(r"https?:|www\.|\.com|\.io", low):
                    continue
                if any(low in s or s in low for s in inst_spans):
                    continue                       # already captured as INSTITUTION
                if re.fullmatch(r"[\d\W]+", t_raw) or len(t_raw.split()) > 6:
                    continue
                if any(low in s or s in low for s in org_spans):
                    continue
                org_spans.append(low)
                add(t_raw, "ORGANIZATION", src_label)
            elif label == "LOCATION":
                if any(low in s for s in inst_spans) or re.search(r"\d", t_raw):
                    continue
                if t_raw[0].isupper():
                    add(t_raw, "LOCATION", src_label)
    else:
        # ── GLiNER unavailable: fall back to the regex/spaCy rules ───────────
        for m in _URL_RE.finditer(text.replace("\\", "/")):
            add(m.group(0).rstrip("/"), "URL", "Regex")

        inst_spans, org_spans = [], []
        in_experience = False
        for line in lines:
            if _EXPERIENCE_HEADERS.match(line):
                in_experience = True
                continue
            if (line and line.strip(":-• \t").isupper() and len(line.split()) <= 4
                    and not _EXPERIENCE_HEADERS.match(line)):
                in_experience = False  # a new ALL-CAPS section header ends Experience

            for m in _INSTITUTION_RE.finditer(line):
                inst_spans.append(m.group(0).lower())
                add(m.group(0), "INSTITUTION", "Regex")
            for m in _DEGREE_ENT_RE.finditer(line):
                add(m.group(1), "DEGREE", "Regex")
            for m in _ORG_SUFFIX_RE.finditer(line):
                cand = m.group(1)
                if not _is_tech_or_noise(cand):
                    org_spans.append(cand.lower())
                    add(cand, "ORGANIZATION", "Regex")
            if in_experience and len(line.split()) <= 16:
                for m in _EXP_LINE_ORG_RE.finditer(line):
                    cand = _norm_ws(m.group(1))
                    low = cand.lower()
                    if (cand and not _is_tech_or_noise(cand) and len(cand.split()) <= 5
                            and not any(low in s or s in low for s in org_spans)
                            and not _INSTITUTION_KW.search(cand)):
                        org_spans.append(low)
                        add(cand, "ORGANIZATION", "Regex")
            if len(line.split()) <= 14:
                for m in _TITLE_RE.finditer(line):
                    words = m.group(1).split()
                    while words and words[0].lower() in _TITLE_FILLER:
                        words.pop(0)
                    if words and not _is_tech_or_noise(" ".join(words)) and len(words) <= 5:
                        add(" ".join(words), "JOB_TITLE", "Regex")

        for ent in doc.ents:
            t = _norm_ws(ent.text)
            low = t.lower()
            if len(t) < 2 or _is_tech_or_noise(t) or "@" in t or re.search(r"https?:|www\.|\.com|\.io", low):
                continue
            if ent.label_ == "PERSON":
                t_check = t.title() if t.isupper() else t
                if _looks_like_name(t_check) and not any(w in _SKILL_TERMS or w in _NOISE_WORDS
                                                          for w in low.split()):
                    add(t_check, "PERSON", "spaCy")
            elif ent.label_ == "ORG":
                if any(low in s or s in low for s in inst_spans) or any(low in s or s in low for s in org_spans):
                    continue
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

    # ── 3. DATE supplement from spaCy (regex already found the common patterns)
    for ent in doc.ents:
        if ent.label_ != "DATE":
            continue
        t = _norm_ws(ent.text)
        low = t.lower()
        if len(t) < 2 or _is_tech_or_noise(t):
            continue
        if any(low in d or d in low for d in date_spans):
            continue
        if re.search(r"(?:19|20)\d{2}", t) and len(re.sub(r"\D", "", t)) < 9:
            add(t, "DATE", "spaCy")

    out = _merge_structure(text, out)
    order = {"PERSON":0,"EMAIL":1,"PHONE":2,"URL":3,"INSTITUTION":4,"ORGANIZATION":5,
             "LOCATION":6,"DEGREE":7,"JOB_TITLE":8,"DATE":9,"SKILL":10}
    out.sort(key=lambda d: (order.get(d["label"], 99), d["entity"].lower()))
    return out


# ══════════════════════════════════════════════════════════════════════════════
# Job role extraction from a Job Description
# ══════════════════════════════════════════════════════════════════════════════

_JD_LABEL_RE = re.compile(
    r"(?i)^\W*(?:job\s*title|job\s*role(?:\s*name)?|role(?:\s*name)?|position(?:\s*applied\s*for)?|"
    r"designation(?:\s*applied\s*for)?|title|opening|vacancy|hiring\s*for|post(?:\s*applied\s*for)?|"
    r"profile|profile\s*offered|role\s*offered|job\s*opening|internship\s*(?:role|profile|program|title)?|"
    r"applying\s*(?:for|position)|post\s*applied)\s*[:\-–—]\s*(.+)$")
_JD_PHRASE_RE = re.compile(
    rf"(?i)(?:looking\s+for|seeking|hiring(?:\s+for)?|currently\s+hiring|we'?re\s+hiring|"
    rf"searching\s+for|opening\s+for|immediate\s+opening\s+for|urgent(?:ly)?\s+(?:hiring|requirement)\s+for|"
    rf"applications?\s+(?:are\s+)?(?:invited|open)\s+for|applications?\s+for|role\s+of|position\s+of|"
    rf"join\s+(?:us|our\s+team)\s+as|apply\s+for|recruiting(?:\s+for)?|looking\s+to\s+hire|in\s+need\s+of)\s+"
    rf"(?:an?\s+|the\s+)?((?:[\w\.+#/&\-]+\s+){{0,5}}?{_TITLE_NOUNS_PLURAL})\b")
_JD_SPLIT_RE = re.compile(r"\s+[-–—|@]\s+|\s*[|•·]\s*|\s+at\s+|\s+in\s+|\s*\(|\s*,\s*|\s*/\s*(?=[A-Z])|\s+for\s+")
# Employment-type / metadata labels that look like a role label but never carry a
# job title -- JDs often list these right next to the real title, so excluding
# them keeps "Employment Type: Full-time" from being mistaken for a role.
_JD_NOT_A_ROLE = {"full-time","full time","part-time","part time","remote","hybrid",
                  "on-site","onsite","contract","permanent","temporary","wfh",
                  "immediate","asap","open","yes","no","n/a","na"}


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


def _title_from_line(line):
    """Find a title-noun phrase anywhere in a raw line and trim leading filler
    words from the match itself (not from a pre-split line), so a sentence like
    "Urgent requirement for Java Developer in Pune" yields "Java Developer"
    rather than swallowing the connective words in front of it."""
    m = _TITLE_RE_LOOSE.search(line)
    if not m:
        return None
    words = m.group(1).split()
    while words and words[0].lower() in _TITLE_FILLER:
        words.pop(0)
    if not words:
        return None
    cand = _norm_ws(" ".join(words))
    if cand.isupper() or cand.islower():
        cand = cand.title()
    return cand


def extract_job_role(jd_text):
    """Best-effort job role/title from a job description; None if not detectable.

    Mirrors how ATS platforms (Greenhouse, Lever, Workday-style postings) and
    recruiter-pasted JDs typically present the role, in order of reliability:
      1. A labelled field ("Job Title:", "Role:", "Position Applied For:", ...)
      2. The JD's very first line, when it stands alone as a short heading
         (ATS postings almost always open with the title before company/location)
      3. Any other short heading line near the top that is itself a title
      4. A natural-language phrase ("we are looking for a ...", "hiring for ...")
      5. The most frequent title-like phrase in the opening of the JD
    Internship, co-op and trainee roles are matched the same way as full-time
    titles throughout, and employment-type words (Full-time, Remote, Contract)
    are filtered out so they're never mistaken for the title itself.
    """
    if not jd_text or not jd_text.strip():
        return None
    lines = [l.strip() for l in jd_text.splitlines() if l.strip()]

    def valid(r):
        return r and r.lower() not in _JD_NOT_A_ROLE and not _is_tech_or_noise(r)

    # 1) labelled field, anywhere in the first 40 non-empty lines
    for l in lines[:40]:
        m = _JD_LABEL_RE.match(l)
        if m:
            r = _clean_role(m.group(1))
            if valid(r):
                return r

    # 2) the JD's own first line, if it reads as a standalone title heading --
    #    this is how most job-board postings present the role, with no label at
    #    all ("Software Development Engineer Intern" as line 1, company/location
    #    following on later lines). Also handles an unlabelled prefix like
    #    "Hiring: Software Engineer Intern" by pulling the title phrase out of
    #    the line rather than trusting the whole line.
    if lines:
        first = lines[0]
        if len(first.split()) <= 12 and not first.endswith((".", ":")):
            r = _title_from_line(first)
            if valid(r):
                return r
            # a standalone line elsewhere that is exactly a title ("Product Manager Intern")
            # beats a tagline on line 1 ("Unlocking the Power of Ownership")
            for l in lines[1:70]:
                if len(l.split()) <= 6 and not re.search(r"[.:;,!?]$", l):
                    r2 = _title_from_line(l)
                    if valid(r2) and r2.lower() == _clean_role(l).lower():
                        return r2
            # no recognised title noun anywhere but line 1 still reads like a bare
            # heading (short, no sentence punctuation) -- accept it as-is.
            cleaned = _clean_role(first)
            if valid(cleaned) and len(lines) > 1 and len((cleaned or "").split()) <= 6:
                return cleaned

    # 3) any other short heading line near the top that is itself a title
    for l in lines[1:8]:
        if len(l.split()) <= 12 and not l.endswith("."):
            r = _title_from_line(l)
            if valid(r):
                return r

    # 4) natural-language phrase ("looking for a ...", "hiring for ...",
    #    "currently hiring Data Science Interns", "urgent requirement for ...")
    m = _JD_PHRASE_RE.search(jd_text[:3000])
    if m:
        r = _clean_role(m.group(1))
        if valid(r):
            return r
    for l in lines[:40]:
        r = _title_from_line(l) if re.search(r"(?i)requirement|urgent|recruiting", l) else None
        if valid(r):
            return r

    # 5) most frequent title-like phrase (loose matcher, case/plural tolerant),
    #    scanned per line so a match can never straddle two unrelated lines
    counts = {}
    for l in lines[:30]:
        if len(l.split()) > 20:        # skip long prose paragraphs, keep headings/bullets
            continue
        cand = _title_from_line(l)
        if cand and valid(cand):
            counts[cand] = counts.get(cand, 0) + 1
    if counts:
        return max(counts, key=lambda k: (counts[k], len(k)))
    return None

# ── section splitting ────────────────────────────────────────────────────────

SECTION_HEADERS = {
    "summary":        r"(?i)^\s*(summary|professional\s*summary|career\s*summary|objective|career\s*objective|profile|professional\s*profile|about\s*me|introduction|overview)\s*$",
    "education":      r"(?i)^\s*(education|educational\s*(background|qualifications?)|academics?|academic\s*(background|qualifications?)|qualifications?|schooling)\s*$",
    "experience":     r"(?i)^\s*((work|professional|employment|relevant|industry)\s*(experience|history)|experience|employment|career(\s*history)?|internships?|positions?(\s*held)?|professional\s*background)\s*$",
    "skills":         r"(?i)^\s*(skills?|technical\s*skills?|key\s*skills?|core\s*(skills?|competenc\w+)|competenc\w+|technologies|tools|tools\s*(&|and)\s*technologies|frameworks?|skills?\s*(&|and)\s*(tools|technologies)|areas?\s*of\s*expertise|expertise)\s*$",
    "languages":      r"(?i)^\s*(languages?|languages?\s*known|language\s*proficiency|linguistic\s*skills?)\s*$",
    "projects":       r"(?i)^\s*(projects?|project\s*work|portfolio|side\s*projects?|personal\s*projects?|academic\s*projects?|key\s*projects?|notable\s*projects?|selected\s*projects?)\s*$",
    "certifications": r"(?i)^\s*(certif\w*(\s*(&|and)\s*(accomplishments|licenses?|courses?))?|licenses?(\s*(&|and)\s*certif\w*)?|credentials?)\s*$",
    "courses":        r"(?i)^\s*(courses?|training|trainings?|coursework|courses?\s*(&|and)\s*training)\s*$",
    "achievements":   r"(?i)^\s*((key\s*)?achievements?|awards?(\s*(&|and)\s*(honou?rs|achievements?|recognitions?))?|honou?rs?|accomplishments?|recognitions?|academic\s*and\s*extracurricular\s*achievements?)\s*$",
    "other_headers":  r"(?i)^\s*(extra[\s\-]*curricul\w*(\s*(&|and)?\s*(activities|leadership))?|activities|leadership|interests?|hobbies|hobbies\s*(&|and)\s*interests?|references?|declaration|publications?|volunteer\w*(\s*experience)?|personal\s*(details|information)|contact(\s*(details|information))?)\s*$",
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
    r"((?:B\.?Tech|B\.?E\.?|B\.?Sc?\.?|M\.?Tech|M\.?Sc?\.?|MBA|Ph\.?D\.?|"
    r"B\.?A\.?|M\.?A\.?|BCA|MCA)(?![A-Za-z])|"
    r"Bachelor|Master|Doctorate|Associate|Diploma)"
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

def analyse_structure(raw_text):
    """Parse every section of a resume into structured entries (see src/structure.py)."""
    from src import structure as st
    sections = split_sections(raw_text)
    name = extract_name_spacy(raw_text)
    hl = st.header_lines(raw_text)
    headline = st.extract_headline(hl, name)
    if headline and headline.isupper():
        headline = headline.title()

    exp = st.parse_experience(sections.get("experience", ""))
    for c in st.parse_experience(sections.get("courses", "")):
        c["kind"] = "Course"
        exp.append(c)
    if not exp and sections.get("experience", "").strip():
        exp = extract_experience(sections["experience"])

    edu = st.parse_education(sections.get("education", ""))
    if not edu:
        edu = extract_education(sections.get("education", "") or raw_text)

    proj = []
    ptxt = sections.get("projects", "")
    if ptxt.strip():
        items = st.parse_titled_items(ptxt)
        if items:
            for it in items:
                proj.append(it["title"] + (f" - {it['subtitle']}" if it.get("subtitle") else "")
                            + (f" ({it['dates']})" if it["dates"] else "")
                            + (": " + it["description"] if it["description"] else ""))
        else:
            proj = extract_projects(ptxt, raw_text)
    else:
        proj = extract_projects("", raw_text)

    certs = st.parse_certifications(sections.get("certifications", ""))
    if not st.parse_experience(sections.get("courses", "")) and sections.get("courses", "").strip():
        certs += st.parse_certifications(sections["courses"])
    ach = st.parse_achievements(sections.get("achievements", ""))

    skills_txt = sections.get("skills", "")
    lang_txt = sections.get("languages", "")
    listed = st.parse_listed_skills(skills_txt)
    spoken = st.parse_languages(lang_txt) or st.parse_languages(skills_txt)
    # a "Languages" section often lists programming languages too: keep those as listed skills
    for it in st.parse_listed_skills(lang_txt):
        if it.lower() not in {x.lower() for x in listed}:
            listed.append(it)

    summary = re.sub(r"\s+", " ", sections.get("summary", "")).strip() or st.extract_summary_fallback(sections.get("other", ""), name, headline)
    location = st.extract_header_location(hl)
    return {"sections": sections, "name": name, "headline": headline, "experience": exp,
            "education": edu, "projects": proj, "certifications": certs, "achievements": ach,
            "listed_skills": listed, "spoken_languages": spoken, "summary": summary,
            "location": location}


def _filter_ambiguous(skills, raw_text, a):
    """'r', 'c', 'go' are also ordinary letters/words: keep them only when they sit in
    the skills section or on a line that lists other skills."""
    sec = (a["sections"].get("skills") or "") + "\n" + (a["sections"].get("languages") or "")
    keep = []
    for sk in skills:
        if sk not in {"r", "c", "go"}:
            keep.append(sk); continue
        pat = re.compile(r"(?<![\w\-+#])" + ("[Rr]" if sk == "r" else "[Cc]" if sk == "c" else "[Gg]o") + r"(?![\w\-+#])")
        if sk != "go" and pat.search(sec):
            keep.append(sk); continue
        for line in raw_text.splitlines():
            if pat.search(line) and len(set(extract_skills(pat.sub(" ", line))) - {sk}) >= 2:
                keep.append(sk); break
    return keep


def parse_resume(file_path):
    raw_text  = extract_text(file_path)
    # Pull hyperlinks that may not appear as plain text (clickable icons in PDFs/DOCX)
    hyperlinks = get_extra_urls(file_path)
    # Append hyperlink URLs to the search corpus for contact field extraction
    contact_corpus = raw_text + "\n" + "\n".join(hyperlinks)

    a = analyse_structure(raw_text)
    from src import structure as _st
    used_ocr = bool(_st.LAST_OCR) if Path(file_path).suffix.lower() == ".pdf" else False
    ents = extract_resume_entities(raw_text)
    orgs = [e["entity"] for e in ents if e["label"] in ("ORGANIZATION", "INSTITUTION")]
    return {
        "raw_text":       raw_text,
        "ocr":            used_ocr,
        "name":           _name_from_email(a["name"], extract_email(contact_corpus)),
        "headline":       a["headline"],
        "email":          extract_email(contact_corpus),
        "phone":          extract_phone(contact_corpus),
        "linkedin":       extract_linkedin(contact_corpus),
        "github":         extract_github(contact_corpus),
        "location":       a["location"],
        "skills":         _filter_ambiguous(extract_skills(raw_text), raw_text, a),
        "listed_skills":  a["listed_skills"],
        "languages":      a["spoken_languages"],
        "education":      a["education"],
        "experience":     a["experience"],
        "projects":       a["projects"],
        "certifications": a["certifications"],
        "achievements":   a["achievements"],
        "summary":        a["summary"],
        "organisations":  orgs,
    }
