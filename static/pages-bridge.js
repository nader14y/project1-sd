"use strict";

// Only the Pages build includes this adapter. Flask keeps using its HTTP API.
(() => {
  const key = "quiz-battle:pages:v1";
  const directory = new URL("../", document.currentScript.src);
  const pyodideURL = "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/";
  let initialization = null;
  let memory = null;
  let queue = Promise.resolve();
  let storageFailed = false;

  async function resource(name) {
    const response = await fetch(new URL(name, directory), { cache: "no-cache", signal: AbortSignal.timeout(30000) });
    if (!response.ok) throw new Error(`Could not load ${name} (${response.status})`);
    return response.text();
  }

  async function initialize() {
    if (initialization) return initialization;
    initialization = (async () => {
      if (typeof loadPyodide !== "function") {
        await new Promise((resolve, reject) => {
          const script = document.createElement("script");
          script.src = `${pyodideURL}pyodide.js`;
          script.onload = resolve;
          script.onerror = () => { script.remove(); reject(new Error("Python runtime download failed")); };
          document.head.append(script);
        });
      }
      const modules = ["engine.py", "storage.py", "web_game.py", "pages_runtime.py", "questions.json"];
      const [python, sources] = await Promise.all([
        loadPyodide({ indexURL: pyodideURL }),
        Promise.all(modules.map(resource)),
      ]);
      python.FS.mkdirTree("/quiz/data");
      modules.forEach((name, index) => python.FS.writeFile(`/quiz/${name}`, sources[index]));
      python.runPython("import sys\nimport logging\nlogging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(levelname)s %(name)s: %(message)s')\nsys.path.insert(0, '/quiz')\nfrom pages_runtime import BrowserRuntime\n_browser = BrowserRuntime('/quiz/questions.json', '/quiz/data')");
      return python;
    })();
    try {
      return await initialization;
    } catch (error) {
      initialization = null;
      console.error("Quiz runtime initialization failed", error);
      throw new Error("موتور بازی دریافت نشد. اتصال اینترنت را بررسی کنید و دوباره تلاش کنید؛ دریافت اولیه ممکن است کمی طول بکشد.");
    }
  }

  function readSaved() {
    try {
      const saved = localStorage.getItem(key);
      return saved ?? memory;
    } catch {
      storageFailed = true;
      return memory;
    }
  }

  async function dispatch(path, body) {
    const python = await initialize();
    const operation = async () => {
      python.globals.set("quiz_browser_request", JSON.stringify({ path, body, saved: readSaved() }));
      let result;
      try {
        result = JSON.parse(python.runPython("_browser.dispatch_json(quiz_browser_request)"));
      } catch (error) {
        console.error("Quiz local request failed", error);
        throw new Error("اجرای بازی با خطا روبه‌رو شد. دوباره تلاش کنید.");
      } finally {
        python.globals.delete("quiz_browser_request");
      }
      memory = result.saved;
      try {
        localStorage.setItem(key, memory);
        storageFailed = false;
      } catch (error) {
        storageFailed = true;
        console.warn("Quiz browser storage unavailable", error);
      }
      if (result.status >= 400) {
        const error = new Error(result.data.error.message);
        error.status = result.status;
        throw error;
      }
      if (storageFailed) {
        result.data.storage_warning = "ذخیره‌سازی مرورگر در دسترس نیست؛ با بستن یا تازه‌سازی صفحه، نتیجه‌ها ممکن است پاک شوند.";
      }
      return result.data;
    };
    if (navigator.locks) return navigator.locks.request(key, operation);
    // Older browsers still serialize requests within this tab.
    return operation();
  }

  window.quizLocalRequest = (path, body) => {
    const task = queue.then(() => dispatch(path, body));
    queue = task.catch(() => {});
    return task;
  };
})();
