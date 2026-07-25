/* Bilingual FR / EN. Choice is stored in localStorage and applied on load.
   Text nodes use data-i18n, HTML fragments use data-i18n-html,
   attributes use data-i18n-attr="attr:key,attr:key". */

const I18N = {
  fr: {
    "meta.title": "AskMyDocs · Assistant documentaire RAG",
    "meta.desc":
      "Assistant documentaire RAG : posez vos questions en langage naturel, obtenez des réponses fondées sur vos propres fichiers CSV et PDF.",

    "nav.overview": "Aperçu",
    "nav.how": "Fonctionnement",
    "nav.methods": "Méthodes",
    "nav.code": "Code",

    "hero.eyebrow": "Assistant documentaire RAG",
    "hero.h1": "Posez la question.<br><em>Vos documents répondent.</em>",
    "hero.lede":
      "AskMyDocs indexe vos fichiers CSV et PDF en local, retrouve les passages les plus pertinents pour votre question, puis rédige une réponse fondée sur eux, sources à l'appui.",
    "hero.cta1": "Voir le code",
    "hero.cta2": "Comment ça marche",
    "hero.note": "Ce site n'utilise ni cookie, ni traceur, ni requête externe.",

    "demo.title": "askmydocs",
    "demo.q": "De quoi parle le film Titanic ?",
    "demo.srcLabel": "Passage retrouvé",
    "demo.file": "Movie_Collection.csv · ligne 218",
    "demo.score": "pertinence 0.94",
    "demo.srcText":
      "Titre : Titanic. Résumé : à bord du paquebot, <mark class=\"hl\">Jack, un artiste sans le sou, et Rose, une jeune aristocrate</mark>, vivent une histoire d'amour interrompue par le naufrage.",
    "demo.ansLabel": "Réponse",
    "demo.answer":
      "Titanic raconte la romance entre <strong>Jack et Rose</strong> à bord du paquebot, jusqu'au naufrage. <span class=\"cite\">source : ligne 218</span>",

    "ov.eyebrow": "Aperçu",
    "ov.h2": "Un assistant qui s'appuie sur vos propres fichiers",
    "ov.p":
      "Chargez vos documents, choisissez une méthode de recherche, posez vos questions en langage naturel.",
    "ov.c1t": "CSV et PDF",
    "ov.c1p":
      "Importez plusieurs fichiers à la fois. Les tableaux comme les documents texte sont découpés en passages exploitables.",
    "ov.c2t": "Réponses sourcées",
    "ov.c2p":
      "Chaque réponse s'accompagne des passages retrouvés et de leur score de pertinence : vous voyez d'où vient l'information.",
    "ov.c3t": "Indexation locale",
    "ov.c3p":
      "L'encodage et la recherche vectorielle s'exécutent sur votre machine avec FAISS ; vos fichiers ne partent pas se faire indexer ailleurs.",

    "how.eyebrow": "Fonctionnement",
    "how.h2": "De la question à la réponse, en quatre temps",
    "how.s1t": "Import",
    "how.s1p": "Vos CSV et PDF sont lus, puis découpés en passages de taille homogène.",
    "how.s2t": "Indexation",
    "how.s2p": "Chaque passage est transformé en vecteur et rangé dans un index FAISS.",
    "how.s3t": "Recherche",
    "how.s3p": "La question est comparée à l'index pour remonter les passages les plus proches.",
    "how.s4t": "Réponse",
    "how.s4p": "Le modèle de langage rédige une réponse fondée sur ces passages.",

    "me.eyebrow": "Méthodes de recherche",
    "me.h2": "Trois stratégies de recherche, un même objectif",
    "me.p": "Choisissez la méthode selon la taille du corpus et la précision recherchée.",
    "me.m1name": "Recherche dense",
    "me.m1tag": "Vecteur",
    "me.m1p":
      "Embeddings multilingues normalisés et recherche vectorielle FAISS (cosinus). Rapide, bonne base.",
    "me.m2name": "Recherche hybride",
    "me.m2tag": "Dense + BM25",
    "me.m2p":
      "Combine la recherche dense et BM25 (mots-clés), fusionnées par Reciprocal Rank Fusion. Meilleure couverture.",
    "me.m3name": "Reranking",
    "me.m3tag": "Cross-encoder",
    "me.m3p":
      "Rappel hybride, puis reclassement des candidats par un cross-encoder pour la précision maximale.",

    "st.eyebrow": "Sous le capot",
    "st.h2": "Construit avec des briques éprouvées",
    "st.p":
      "Un socle Python, une interface Streamlit et l'écosystème open source de la recherche vectorielle.",
    "st.e1t": "Confidentiel par défaut",
    "st.e1p":
      "Indexation et recherche en local ; ce site ne dépose aucun cookie et n'appelle aucun service tiers.",
    "st.e2t": "Recherche testée",
    "st.e2p":
      "Un test d'aller-retour vérifie qu'une question retrouve bien, en tête, le passage attendu.",
    "st.e3t": "Multi-plateforme",
    "st.e3p": "Des lanceurs prêts à l'emploi pour Windows et pour Linux ou macOS.",

    "cta.h2": "Le projet est open source",
    "cta.p":
      "Parcourez le code, lancez l'assistant en local, ou lisez le rapport qui détaille la démarche.",
    "cta.b1": "Voir sur GitHub",
    "cta.b2": "Lire le rapport (PDF)",
    "cta.download": "Télécharger le code (ZIP)",
    "cta.eyebrow": "Le code",
    "ov.metaRun": "CSV · PDF · réponses sourcées",
    "how.p2": "Un pipeline simple, du fichier brut jusqu'à la réponse fondée sur vos passages.",
    "me.metaRun": "3 stratégies interchangeables",
    "me.thMethod": "Méthode",
    "me.thDesc": "Description",
    "me.thBest": "Idéal pour",
    "me.m1best": "base rapide",
    "me.m2best": "meilleure couverture",
    "me.m3best": "précision maximale",
    "demo.fig": "Un passage retrouvé et la réponse qui s'appuie dessus",
    "st.stackLine": "<b>Python</b> · Streamlit · FAISS · sentence-transformers · cross-encoder · BM25 · Mistral AI · pdfplumber · NumPy · pandas",

    "ft.tagline":
      "Assistant documentaire RAG. Projet personnel, réalisé dans un cadre académique à CY Tech (2024-2025).",
    "ft.col1": "Projet",
    "ft.col2": "Ressources",
    "ft.code": "Code source",
    "ft.report": "Rapport (PDF)",
    "ft.legal": "Mentions légales",
    "ft.rights": "© 2026 Abdellah Hassani. Tous droits réservés.",
    "ft.privacy": "Sans cookie · Sans traceur · Hébergé en France",

    "lg.back": "Retour à l'accueil",
    "lg.eyebrow": "Informations légales",
    "lg.h1": "Mentions légales",
    "lg.intro":
      "Informations légales relatives au site AskMyDocs, conformément à la législation française en vigueur.",
    "lg.1h": "Éditeur du site",
    "lg.1p":
      "Le site est édité par Abdellah Hassani, à titre personnel. Directeur de la publication : Abdellah Hassani. Contact : <a href=\"mailto:abdellah.hassani2002@gmail.com\">abdellah.hassani2002@gmail.com</a>.",
    "lg.2h": "Hébergement",
    "lg.2p":
      "Le site est hébergé par OVH SAS, 2 rue Kellermann, 59100 Roubaix, France. RCS Lille Métropole 424 761 419 00045. Les serveurs sont situés en France.",
    "lg.3h": "Données personnelles",
    "lg.3p":
      "Ce site n'utilise aucun cookie, aucun traceur et ne collecte aucune donnée personnelle. Il ne fait appel à aucun service tiers : l'ensemble du traitement s'exécute localement, dans votre navigateur.",
    "lg.4h": "Propriété intellectuelle",
    "lg.4p":
      "Le code source du projet est publié sur GitHub : <a href=\"https://github.com/Abdellah427/AskMyDocs\">github.com/Abdellah427/AskMyDocs</a>. Le nom du projet, les textes et l'interface de ce site sont l'œuvre d'Abdellah Hassani.",
    "lg.5h": "Responsabilité",
    "lg.5p":
      "Le projet est fourni « en l'état », sans garantie d'aucune sorte, expresse ou implicite. L'éditeur ne saurait être tenu responsable d'un éventuel dommage lié à son utilisation.",
    "lg.updated": "Dernière mise à jour : juillet 2026",
    "lg.metaTitle": "Mentions légales · AskMyDocs",
    "lg.metaDesc": "Mentions légales du site AskMyDocs.",
  },

  en: {
    "meta.title": "AskMyDocs · RAG document assistant",
    "meta.desc":
      "RAG document assistant: ask questions in plain language and get answers grounded in your own CSV and PDF files.",

    "nav.overview": "Overview",
    "nav.how": "How it works",
    "nav.methods": "Methods",
    "nav.code": "Code",

    "hero.eyebrow": "RAG document assistant",
    "hero.h1": "Ask the question.<br><em>Your documents answer.</em>",
    "hero.lede":
      "AskMyDocs indexes your CSV and PDF files locally, retrieves the passages most relevant to your question, then writes an answer grounded in them, sources included.",
    "hero.cta1": "View the code",
    "hero.cta2": "How it works",
    "hero.note": "This site uses no cookies, no trackers and no external requests.",

    "demo.title": "askmydocs",
    "demo.q": "What is the movie Titanic about?",
    "demo.srcLabel": "Retrieved passage",
    "demo.file": "Movie_Collection.csv · row 218",
    "demo.score": "relevance 0.94",
    "demo.srcText":
      "Title: Titanic. Summary: aboard the liner, <mark class=\"hl\">Jack, a penniless artist, and Rose, a young aristocrat</mark>, live a love story cut short by the sinking.",
    "demo.ansLabel": "Answer",
    "demo.answer":
      "Titanic tells the romance between <strong>Jack and Rose</strong> aboard the liner, up to the sinking. <span class=\"cite\">source: row 218</span>",

    "ov.eyebrow": "Overview",
    "ov.h2": "An assistant that builds on your own files",
    "ov.p": "Upload your documents, pick a retrieval method, ask your questions in plain language.",
    "ov.c1t": "CSV and PDF",
    "ov.c1p":
      "Import several files at once. Spreadsheets and text documents alike are split into searchable passages.",
    "ov.c2t": "Grounded answers",
    "ov.c2p":
      "Every answer comes with the retrieved passages and their relevance score: you see where the information comes from.",
    "ov.c3t": "Local indexing",
    "ov.c3p":
      "Embedding and vector search run on your machine with FAISS; your files are not shipped off to be indexed elsewhere.",

    "how.eyebrow": "How it works",
    "how.h2": "From question to answer, in four steps",
    "how.s1t": "Upload",
    "how.s1p": "Your CSV and PDF files are read, then split into evenly sized passages.",
    "how.s2t": "Index",
    "how.s2p": "Each passage is turned into a vector and stored in a FAISS index.",
    "how.s3t": "Retrieve",
    "how.s3p": "Your question is matched against the index to surface the closest passages.",
    "how.s4t": "Answer",
    "how.s4p": "The language model writes an answer grounded in those passages.",

    "me.eyebrow": "Retrieval methods",
    "me.h2": "Three retrieval strategies, one goal",
    "me.p": "Pick the method based on corpus size and the precision you need.",
    "me.m1name": "Dense search",
    "me.m1tag": "Vector",
    "me.m1p":
      "Normalized multilingual embeddings with FAISS cosine search. Fast, a solid baseline.",
    "me.m2name": "Hybrid search",
    "me.m2tag": "Dense + BM25",
    "me.m2p":
      "Combines dense search and BM25 (keywords), fused with Reciprocal Rank Fusion. Better coverage.",
    "me.m3name": "Reranking",
    "me.m3tag": "Cross-encoder",
    "me.m3p":
      "Hybrid recall, then a cross-encoder re-ranks the candidates for top precision.",

    "st.eyebrow": "Under the hood",
    "st.h2": "Built on proven building blocks",
    "st.p":
      "A Python core, a Streamlit interface and the open-source vector-search ecosystem.",
    "st.e1t": "Private by default",
    "st.e1p":
      "Indexing and search run locally; this site sets no cookies and calls no third-party service.",
    "st.e2t": "Tested retrieval",
    "st.e2p":
      "A round-trip test verifies that a question brings back the expected passage at the top.",
    "st.e3t": "Cross-platform",
    "st.e3p": "Ready-to-use launchers for Windows and for Linux or macOS.",

    "cta.h2": "The project is open source",
    "cta.p":
      "Browse the code, run the assistant locally, or read the report that details the approach.",
    "cta.b1": "View on GitHub",
    "cta.b2": "Read the report (PDF)",
    "cta.download": "Download the code (ZIP)",
    "cta.eyebrow": "The code",
    "ov.metaRun": "CSV · PDF · grounded answers",
    "how.p2": "A simple pipeline, from the raw file to an answer grounded in your passages.",
    "me.metaRun": "3 interchangeable strategies",
    "me.thMethod": "Method",
    "me.thDesc": "Description",
    "me.thBest": "Best for",
    "me.m1best": "fast baseline",
    "me.m2best": "better coverage",
    "me.m3best": "top precision",
    "demo.fig": "A retrieved passage and the answer grounded in it",
    "st.stackLine": "<b>Python</b> · Streamlit · FAISS · sentence-transformers · cross-encoder · BM25 · Mistral AI · pdfplumber · NumPy · pandas",

    "ft.tagline":
      "RAG document assistant. A personal project, built in an academic setting at CY Tech (2024-2025).",
    "ft.col1": "Project",
    "ft.col2": "Resources",
    "ft.code": "Source code",
    "ft.report": "Report (PDF)",
    "ft.legal": "Legal notice",
    "ft.rights": "© 2026 Abdellah Hassani. All rights reserved.",
    "ft.privacy": "No cookies · No trackers · Hosted in France",

    "lg.back": "Back to home",
    "lg.eyebrow": "Legal information",
    "lg.h1": "Legal notice",
    "lg.intro":
      "Legal information about the AskMyDocs site, in accordance with applicable French law.",
    "lg.1h": "Site publisher",
    "lg.1p":
      "This site is published by Abdellah Hassani, in a personal capacity. Publication director: Abdellah Hassani. Contact: <a href=\"mailto:abdellah.hassani2002@gmail.com\">abdellah.hassani2002@gmail.com</a>.",
    "lg.2h": "Hosting",
    "lg.2p":
      "The site is hosted by OVH SAS, 2 rue Kellermann, 59100 Roubaix, France. RCS Lille Métropole 424 761 419 00045. The servers are located in France.",
    "lg.3h": "Personal data",
    "lg.3p":
      "This site uses no cookies, no trackers and collects no personal data. It relies on no third-party service: all processing runs locally, in your browser.",
    "lg.4h": "Intellectual property",
    "lg.4p":
      "The project's source code is published on GitHub: <a href=\"https://github.com/Abdellah427/AskMyDocs\">github.com/Abdellah427/AskMyDocs</a>. The project name, the texts and the interface of this site are the work of Abdellah Hassani.",
    "lg.5h": "Liability",
    "lg.5p":
      "The project is provided “as is”, without warranty of any kind, express or implied. The publisher cannot be held liable for any damage arising from its use.",
    "lg.updated": "Last updated: July 2026",
    "lg.metaTitle": "Legal notice · AskMyDocs",
    "lg.metaDesc": "Legal notice for the AskMyDocs site.",
  },
};

const LANG_KEY = "askmydocs-lang";

function applyLang(lang) {
  const dict = I18N[lang] || I18N.fr;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key] != null) el.textContent = dict[key];
  });

  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    const key = el.getAttribute("data-i18n-html");
    if (dict[key] != null) el.innerHTML = dict[key];
  });

  document.querySelectorAll("[data-i18n-attr]").forEach((el) => {
    el.getAttribute("data-i18n-attr")
      .split(",")
      .forEach((pair) => {
        const [attr, key] = pair.split(":").map((s) => s.trim());
        if (attr && key && dict[key] != null) el.setAttribute(attr, dict[key]);
      });
  });

  const titleKey = document.documentElement.getAttribute("data-title-key") || "meta.title";
  const descKey = document.documentElement.getAttribute("data-desc-key") || "meta.desc";
  if (dict[titleKey]) document.title = dict[titleKey];
  const desc = document.querySelector('meta[name="description"]');
  if (desc && dict[descKey]) desc.setAttribute("content", dict[descKey]);

  document.documentElement.setAttribute("lang", lang);

  document.querySelectorAll("[data-lang]").forEach((btn) => {
    btn.setAttribute("aria-pressed", String(btn.getAttribute("data-lang") === lang));
  });

  try {
    localStorage.setItem(LANG_KEY, lang);
  } catch (e) {
    /* storage unavailable: fall back to session-only */
  }
}

function initI18n() {
  let lang = "fr";
  try {
    const stored = localStorage.getItem(LANG_KEY);
    if (stored === "fr" || stored === "en") lang = stored;
  } catch (e) {
    /* ignore */
  }

  applyLang(lang);

  document.querySelectorAll("[data-lang]").forEach((btn) => {
    btn.addEventListener("click", () => applyLang(btn.getAttribute("data-lang")));
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initI18n);
} else {
  initI18n();
}
