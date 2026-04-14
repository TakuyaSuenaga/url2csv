import { useState, useEffect } from "react";

const STORAGE = {
  urls: "url-to-csv:urls",
  columns: "url-to-csv:columns",
  data: "url-to-csv:data",
};

function Spinner() {
  return (
    <svg
      className="animate-spin h-4 w-4 text-white inline-block mr-2"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
    </svg>
  );
}

function App() {
  const [urlsInput, setUrlsInput] = useState(() => localStorage.getItem(STORAGE.urls) ?? "");
  const [columnsInput, setColumnsInput] = useState(() => localStorage.getItem(STORAGE.columns) ?? "会社名, 住所");
  const [data, setData] = useState<Record<string, string>[]>([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState<string | null>(null);
  const [errors, setErrors] = useState<string[]>([]);

  useEffect(() => { localStorage.setItem(STORAGE.urls, urlsInput); }, [urlsInput]);
  useEffect(() => { localStorage.setItem(STORAGE.columns, columnsInput); }, [columnsInput]);

  const parseColumns = () => columnsInput.split(",").map((c) => c.trim()).filter(Boolean);
  const parseUrls = () => urlsInput.split("\n").map((u) => u.trim()).filter(Boolean);

  const canSubmit = !loading && parseUrls().length > 0 && parseColumns().length > 0;

  const handleSubmit = async () => {
    const urls = parseUrls();
    const columns = parseColumns();

    if (urls.length === 0) {
      setErrors(["URLを1つ以上入力してください"]);
      return;
    }
    if (columns.length === 0) {
      setErrors(["抽出する項目を1つ以上入力してください"]);
      return;
    }

    setLoading(true);
    setProgress("開始中...");
    setErrors([]);
    setData([]);

    try {
      const res = await fetch("http://localhost:8000/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ urls, columns }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "サーバーエラー" }));
        throw new Error(err.detail ?? "サーバーエラー");
      }

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = JSON.parse(line.slice(6));
          if (payload.type === "progress") {
            setProgress(payload.message);
          } else if (payload.type === "result") {
            setData(payload.data);
          } else if (payload.type === "error") {
            setErrors((prev) => [...prev, payload.message]);
          }
        }
      }
    } catch (e) {
      setErrors([e instanceof Error ? e.message : "予期しないエラーが発生しました"]);
    } finally {
      setLoading(false);
      setProgress(null);
    }
  };

  const handleDownload = () => {
    if (data.length === 0) return;
    const headers = Object.keys(data[0]);
    const rows = data.map((row: Record<string, string>) =>
      headers.map((h) => `"${String(row[h] ?? "").replace(/"/g, '""')}"`).join(",")
    );
    const csv = [headers.join(","), ...rows].join("\n");
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "output.csv";
    link.click();
  };

  const handleClear = () => {
    setData([]);
    setErrors([]);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-8">
      <div className="bg-white p-8 rounded-xl shadow w-full max-w-2xl space-y-5">
        <h1 className="text-xl font-bold text-gray-800">URL → CSV</h1>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            URL（1行に1つ）
          </label>
          <textarea
            className="w-full border border-gray-300 p-2 rounded-lg mt-1 h-32 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            placeholder={"https://example.com/page1\nhttps://example.com/page2"}
            value={urlsInput}
            onChange={(e) => setUrlsInput(e.target.value)}
          />
          {parseUrls().length > 0 && (
            <p className="text-xs text-gray-400 mt-1">{parseUrls().length} 件のURL</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            抽出する項目（カンマ区切り）
          </label>
          <input
            className="w-full border border-gray-300 p-2 rounded-lg mt-1 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            placeholder="例: 会社名, 住所, 電話番号"
            value={columnsInput}
            onChange={(e) => setColumnsInput(e.target.value)}
          />
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg disabled:opacity-40 hover:bg-blue-700 transition-colors font-medium text-sm"
          >
            {loading ? (
              <>
                <Spinner />
                処理中...
              </>
            ) : (
              "抽出"
            )}
          </button>
          {(data.length > 0 || errors.length > 0) && !loading && (
            <button
              onClick={handleClear}
              className="px-4 py-2 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 transition-colors text-sm"
            >
              クリア
            </button>
          )}
        </div>

        {progress && (
          <div className="flex items-center gap-2 text-blue-600 text-sm">
            <Spinner />
            <span>{progress}</span>
          </div>
        )}

        {errors.length > 0 && (
          <div className="border-l-4 border-red-400 bg-red-50 p-3 rounded-r-lg">
            <p className="text-red-700 text-sm font-medium mb-1">エラー</p>
            {errors.map((msg, i) => (
              <p key={i} className="text-red-600 text-sm">{msg}</p>
            ))}
          </div>
        )}

        {data.length > 0 && (
          <>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500 font-medium">{data.length} 件抽出</span>
              <button
                onClick={handleDownload}
                className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700 transition-colors font-medium"
              >
                CSVをダウンロード
              </button>
            </div>

            <div className="overflow-x-auto rounded-lg border border-gray-200">
              <table className="w-full text-sm table-fixed">
                <thead className="bg-gray-100 border-b border-gray-200">
                  <tr>
                    {Object.keys(data[0]).map((k) => (
                      <th key={k} className="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide break-words">
                        {k}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {data.slice(0, 50).map((row: Record<string, string>, i: number) => (
                    <tr key={i} className="hover:bg-gray-50 transition-colors">
                      {Object.values(row).map((v, j) => (
                        <td key={j} className="px-3 py-2 align-top break-words text-gray-700">{v}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {data.length > 50 && (
              <p className="text-xs text-gray-400 text-center">
                表示は50件まで。全 {data.length} 件はCSVをダウンロードしてください。
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default App;
