from __future__ import annotations


CAPABILITY_BRIDGE = (
    (
        "chem.activity_database",
        {
            "prompt_hints": ("chembl", "ic50", "assay", "bioactivity", "活性数据"),
            "skill_inference_hints": ("chembl", "ic50", "assay", "bioactivity", "activity data"),
        },
    ),
    (
        "chem.medchem_filtering",
        {
            "prompt_hints": ("medicinal chemistry", "drug-likeness", "lipinski", "pains", "lead optimization", "药物化学", "先导化合物", "先导优化"),
            "skill_inference_hints": ("medicinal chemistry", "drug-likeness", "lipinski", "pains", "lead optimization", "药物化学", "先导化合物", "先导优化"),
        },
    ),
    (
        "clinical.case_report",
        {
            "prompt_hints": ("clinical report", "care guidelines", "case report", "hipaa", "de-identification", "病例报告", "去标识化"),
            "skill_inference_hints": ("clinical report", "care guidelines", "case report", "hipaa", "de-identification", "病例报告", "去标识化"),
        },
    ),
    (
        "data.eda",
        {
            "prompt_hints": ("eda", "exploratory", "exploratory analysis", "exploratory data analysis", "探索", "探索性"),
            "skill_inference_hints": ("eda", "exploratory", "exploratory analysis", "exploratory data analysis"),
        },
    ),
    (
        "data.quality_check",
        {
            "prompt_hints": ("data quality", "quality check", "missing", "duplicate", "outlier", "数据质量", "缺失", "重复", "异常"),
            "skill_inference_hints": ("data quality", "quality check", "diagnostic", "missing", "duplicate", "outlier"),
        },
    ),
    (
        "debug.systematic_workflow",
        {
            "prompt_hints": ("debug systematically", "failing test", "stack trace", "debug workflow", "系统化调试", "错误日志", "排查", "测试失败", "构建失败", "接口失败", "运行失败"),
            "skill_inference_hints": ("systematic-debugging", "systematic debugging", "debugging test", "debug workflow"),
        },
    ),
    (
        "deploy.netlify",
        {
            "prompt_hints": ("netlify", "deploy to netlify", "部署到netlify"),
            "skill_inference_hints": ("netlify", "preview link", "deploy to netlify"),
        },
    ),
    (
        "deploy.vercel",
        {
            "prompt_hints": ("vercel", "deploy to vercel", "部署到vercel"),
            "skill_inference_hints": ("vercel", "preview deployment", "deploy to vercel"),
        },
    ),
    (
        "devops.github_actions_ci",
        {
            "prompt_hints": ("github actions", "ci failure", "ci失败", "workflow logs", "pr checks"),
            "skill_inference_hints": ("github actions", "failing github pr checks", "pr checks", "workflow logs", "ci failure"),
        },
    ),
    (
        "devops.mcp_integration",
        {
            "prompt_hints": ("mcp", "model context protocol", ".mcp.json", "mcp server", "mcp integration"),
            "skill_inference_hints": ("mcp", "model context protocol", ".mcp.json", "mcp server", "mcp integration"),
        },
    ),
    (
        "document.latex_submission",
        {
            "prompt_hints": ("latex", "latexmk", "chktex", "latexindent", "submission zip", "manuscript pdf"),
            "skill_inference_hints": ("latex", "latexmk", "chktex", "latexindent", "submission", "manuscript"),
        },
    ),
    (
        "document.venue_template",
        {
            "prompt_hints": ("venue template", "venue-specific", "author guidelines", "page limits", "anonymity rules", "formatting requirements", "submission compliance", "neurips", "模板", "匿名投稿", "投稿格式"),
            "skill_inference_hints": ("venue-specific templates", "author guidelines", "page limits", "anonymity rules", "formatting requirements", "submission compliance", "模板", "匿名投稿"),
        },
    ),
    (
        "model.data_leakage_guard",
        {
            "prompt_hints": ("data leakage", "fit before split", "prediction time", "train-test split", "train test split", "数据泄漏"),
            "skill_inference_hints": ("data leakage", "fit before split", "prediction time", "train-test split", "train test split", "leakage"),
        },
    ),
    (
        "model.evaluation",
        {
            "prompt_hints": ("model evaluation", "evaluate model", "metrics", "cross validation", "模型评估", "交叉验证"),
            "skill_inference_hints": ("model evaluation", "metrics", "cross validation"),
        },
    ),
    (
        "model.explainability",
        {
            "prompt_hints": ("shap", "explain", "explanation", "interpretation", "importance", "解释", "可解释", "重要性"),
            "skill_inference_hints": ("shap", "model explanation", "feature importance", "explainability", "interpretation"),
        },
    ),
    (
        "model.preprocessing_pipeline",
        {
            "prompt_hints": ("data preprocessing pipeline", "preprocessing pipeline", "feature encoding", "standardize data", "validate input data", "预处理流水线", "清洗数据"),
            "skill_inference_hints": ("preprocessing pipeline", "data preprocessing pipeline", "cleaning", "encoding", "transforming", "validating input data", "input-preparation pipelines"),
        },
    ),
    (
        "model.training",
        {
            "prompt_hints": ("prediction model", "predictive model", "machine learning", "scikit-learn", "train model", "训练模型", "预测模型", "机器学习"),
            "skill_inference_hints": ("machine learning", "model training", "predictive model", "prediction model", "scikit-learn"),
        },
    ),
    (
        "observability.sentry",
        {
            "prompt_hints": ("sentry", "production error", "线上报错", "线上告警"),
            "skill_inference_hints": ("sentry", "production error", "production errors", "线上报错", "线上告警"),
        },
    ),
    (
        "presentation.deck",
        {
            "prompt_hints": ("ppt", "pptx", "slide", "slides", "deck", "presentation", "幻灯片", "演示文稿", "组会汇报", "汇报"),
            "skill_inference_hints": ("ppt", "pptx", "slide", "slides", "deck"),
        },
    ),
    (
        "presentation.poster",
        {
            "prompt_hints": ("research poster", "academic poster", "conference poster", "poster", "海报", "学术海报"),
            "skill_inference_hints": ("research poster", "academic poster", "conference poster", "poster", "海报", "学术海报"),
        },
    ),
    (
        "presentation.pptx_poster",
        {
            "prompt_hints": ("pptx poster", "powerpoint poster", "ppt poster", "pptx 学术海报", "powerpoint pptx"),
            "skill_inference_hints": ("pptx poster", "powerpoint poster", "ppt poster", "pptx 学术海报", "powerpoint pptx"),
        },
    ),
    (
        "presentation.slidev",
        {
            "prompt_hints": ("slidev", "marp", "reveal.js", "可复现导出"),
            "skill_inference_hints": ("slidev", "marp", "reveal.js", "reproducible export", "可复现导出"),
        },
    ),
    (
        "quality.test_report",
        {
            "prompt_hints": ("pytest", "coverage", "test report", "test reports", "测试报告", "失败摘要", "覆盖率", "质量门禁"),
            "skill_inference_hints": ("test reports", "test-result packaging", "pass/fail rollups", "coverage summaries", "pytest", "coverage"),
        },
    ),
    (
        "research.causal_analysis",
        {
            "prompt_hints": ("causal analysis", "causal effect", "treatment effect", "did", "synthetic control", "因果分析", "因果效应", "稳健性检验"),
            "skill_inference_hints": ("causal analysis", "causal effects", "treatment-effect", "treatment effects", "did", "synthetic control", "因果分析", "因果效应"),
        },
    ),
    (
        "research.citation_management",
        {
            "prompt_hints": ("citation management", "bibliography", "bibtex", "doi", "参考文献"),
            "skill_inference_hints": ("citation management", "bibliography", "bibtex", "doi", "参考文献"),
        },
    ),
    (
        "research.critical_appraisal",
        {
            "prompt_hints": ("critical appraisal", "critical thinking", "bias", "confounding", "批判性", "证据强度", "偏倚", "混杂"),
            "skill_inference_hints": ("critical thinking", "critical appraisal", "bias", "confounding", "证据强度", "偏倚", "混杂"),
        },
    ),
    (
        "research.deep_research",
        {
            "prompt_hints": ("webthinker", "deep research", "multi-hop", "trace.jsonl", "sources.json", "多跳浏览", "证据链"),
            "skill_inference_hints": ("webthinker", "deep research", "multi-hop", "trace.jsonl", "sources.json"),
        },
    ),
    (
        "research.evidence_retrieval",
        {
            "prompt_hints": ("flashrag", "evidence retrieval", "repo/config", "证据检索", "文件和行号"),
            "skill_inference_hints": ("flashrag", "evidence retrieval", "repo/config", "file and line"),
        },
    ),
    (
        "research.experimental_design",
        {
            "prompt_hints": ("experiment design", "study design", "quasi-experiment", "design experiments", "设计准实验", "准实验方案", "实验设计", "实验失败", "验证实验", "设计下一轮"),
            "skill_inference_hints": ("designing-experiments", "experiment design", "study design", "quasi-experiment", "quasi-experiments", "实验设计", "准实验"),
        },
    ),
    (
        "research.hypothesis_generation",
        {
            "prompt_hints": ("hypothesis generation", "testable hypothesis", "hypogenic", "generate hypotheses", "科研假设", "可检验", "假设", "预测"),
            "skill_inference_hints": ("hypothesis-generation", "testable hypotheses", "hypothesis generation", "hypogenic", "generate hypotheses"),
        },
    ),
    (
        "research.ideation",
        {
            "prompt_hints": ("scientific ideation", "research gaps", "literature matrix", "paper-combination", "a+b", "科研构思", "头脑风暴", "研究方向", "论文组合矩阵", "研究创新点"),
            "skill_inference_hints": ("scientific ideation", "research gaps", "mechanism exploration", "research directions", "literature matrix", "paper-combination", "a+b idea"),
        },
    ),
    (
        "research.literature_review",
        {
            "prompt_hints": ("full-text", "systematic review", "literature review", "meta-analysis", "evidence table", "biorxiv", "preprint", "preprints", "系统综述", "文献综述", "证据表", "样本量", "方法学细节"),
            "skill_inference_hints": ("literature-review", "systematic literature review", "meta-analysis", "evidence table", "full-text", "systematic review"),
        },
    ),
    (
        "research.literature_search",
        {
            "prompt_hints": ("pubmed", "bibtex", "mesh", "literature search", "文献检索", "检索", "文献"),
            "skill_inference_hints": ("pubmed", "bibtex", "mesh", "citation management", "literature search", "文献检索"),
        },
    ),
    (
        "research.pubmed_search",
        {
            "prompt_hints": ("pubmed", "mesh"),
            "skill_inference_hints": ("pubmed", "mesh"),
        },
    ),
    (
        "research.scholar_evaluation",
        {
            "prompt_hints": ("scholareval", "rubric", "formulation", "methodology"),
            "skill_inference_hints": ("scholareval", "rubric", "formulation", "methodology"),
        },
    ),
    (
        "research.zotero_management",
        {
            "prompt_hints": ("pyzotero", "zotero library", "zotero"),
            "skill_inference_hints": ("pyzotero", "zotero library", "zotero"),
        },
    ),
    (
        "runtime.node_zombie_cleanup",
        {
            "prompt_hints": ("zombie node", "僵尸node", "node process", "node进程"),
            "skill_inference_hints": ("zombie node", "zombie node processes", "僵尸node", "node process"),
        },
    ),
    (
        "statistics.correlation",
        {
            "prompt_hints": ("correlation", "correlate", "relationship", "trend", "相关", "关联", "趋势"),
            "skill_inference_hints": ("statistical analysis", "统计分析", "correlation", "correlate"),
        },
    ),
    (
        "statistics.regression",
        {
            "prompt_hints": ("regression", "model", "impact", "effect", "relationship", "回归", "建模", "模型"),
            "skill_inference_hints": ("statistical analysis", "统计分析", "regression", "linear model"),
        },
    ),
    (
        "statistics.relationship_modeling",
        {
            "prompt_hints": ("relationship", "relation", "impact", "effect", "compare", "关系", "影响", "比较"),
            "skill_inference_hints": ("statistical analysis", "统计分析", "relationship", "relation", "impact", "effect", "compare"),
        },
    ),
    (
        "visualization.figure",
        {
            "prompt_hints": ("figure", "figures", "chart", "plot", "visual", "matplotlib", "tiff", "图表", "作图", "可视化", "科研绘图", "多子图", "结果图", "投稿图", "绘制"),
            "skill_inference_hints": ("figure", "chart", "plot", "graph", "visualization"),
        },
    ),
    (
        "visualization.infographic",
        {
            "prompt_hints": ("infographic", "infographics", "visual summary", "信息图"),
            "skill_inference_hints": ("infographic", "infographics", "visual summary", "信息图"),
        },
    ),
    (
        "visualization.schematic",
        {
            "prompt_hints": ("schematic", "schematics", "diagram", "diagrams", "flowchart", "flowcharts", "示意图", "流程图", "机制图"),
            "skill_inference_hints": ("schematic", "schematics", "diagram", "diagrams", "flowchart", "flowcharts", "示意图", "流程图"),
        },
    ),
    (
        "writing.reader_report",
        {
            "prompt_hints": ("reader report", "report", "ordinary reader", "plain language", "报告", "普通读者", "通俗"),
            "skill_inference_hints": ("reader report", "plain language", "ordinary reader"),
        },
    ),
    (
        "writing.scientific_report",
        {
            "prompt_hints": ("scientific report", "scientific reporting", "research report", "executive summary", "quarto", "科研报告", "科研技术报告", "科学报告", "实验结果"),
            "skill_inference_hints": ("scientific-reporting", "scientific reporting", "scientific report"),
        },
    ),
)

ROUTER_CAPABILITY_HINTS = tuple(
    (capability, tuple(spec["prompt_hints"]))
    for capability, spec in CAPABILITY_BRIDGE
)

SKILL_INDEX_CAPABILITY_HINTS = tuple(
    (capability, tuple(spec["skill_inference_hints"]))
    for capability, spec in CAPABILITY_BRIDGE
)
