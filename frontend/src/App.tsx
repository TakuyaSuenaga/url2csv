import { useState, useEffect } from "react";

const STORAGE = {
  urls: "url-to-csv:urls",
  columns: "url-to-csv:columns",
  data: "url-to-csv:data",
};

function App() {
  const [urlsInput, setUrlsInput] = useState(() => localStorage.getItem(STORAGE.urls) ?? "");
  const [columnsInput, setColumnsInput] = useState(() => localStorage.getItem(STORAGE.columns) ?? "会社名, 住所");
  const [data, setData] = useState<Record<string, string>[]>([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { localStorage.setItem(STORAGE.urls, urlsInput); }, [urlsInput]);
  useEffect(() => { localStorage.setItem(STORAGE.columns, columnsInput); }, [columnsInput]);

  const parseColumns = () => columnsInput.split(",").map((c) => c.trim()).filter(Boolean);
  const parseUrls = () => urlsInput.split("\n").map((u) => u.trim()).filter(Boolean);

  const handleSubmit = async () => {
    const urls = parseUrls();
    const columns = parseColumns();

    if (urls.length === 0) {
      setError("URLを1つ以上入力してください");
      return;
    }
    if (columns.length === 0) {
      setError("抽出する項目を1つ以上入力してください");
      return;
    }

    setLoading(true);
    setProgress("開始中...");
    setError(null);
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
            setError((prev) => (prev ? `${prev}\n${payload.message}` : payload.message));
          }
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "予期しないエラーが発生しました");
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

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-xl shadow w-full max-w-xl space-y-4">
        <h1 className="text-xl font-bold">URL → CSV</h1>

        <div>
          <label className="text-sm text-gray-600">URL（1行に1つ）</label>
          <textarea
            className="w-full border p-2 rounded mt-1 h-24 resize-none"
            placeholder={"https://example.com/page1\nhttps://example.com/page2"}
            value={urlsInput}
            onChange={(e) => setUrlsInput(e.target.value)}
          />
        </div>

        <div>
          <label className="text-sm text-gray-600">抽出する項目（カンマ区切り）</label>
          <input
            className="w-full border p-2 rounded mt-1"
            placeholder="例: 会社名, 住所, 電話番号"
            value={columnsInput}
            onChange={(e) => setColumnsInput(e.target.value)}
          />
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading || !urlsInput.trim()}
          className="w-full bg-blue-600 text-white p-2 rounded disabled:opacity-50"
        >
          {loading ? "処理中..." : "抽出"}
        </button>

        {progress && (
          <p className="text-blue-600 text-sm">{progress}</p>
        )}

        {error && (
          <p className="text-red-600 text-sm whitespace-pre-line">{error}</p>
        )}

        {data.length > 0 && (
          <>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">{data.length} 件抽出</span>
              <button
                onClick={handleDownload}
                className="bg-green-600 text-white px-4 py-2 rounded text-sm"
              >
                CSVをダウンロード
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm border table-fixed">
                <thead>
                  <tr>
                    {Object.keys(data[0]).map((k) => (
                      <th key={k} className="border p-2 bg-gray-50 text-left align-top break-words">{k}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.slice(0, 50).map((row: Record<string, string>, i: number) => (
                    <tr key={i}>
                      {Object.values(row).map((v, j) => (
                        <td key={j} className="border p-2 align-top break-words">{v}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {data.length > 50 && (
              <p className="text-sm text-gray-400 text-center">
                表示は50件まで。全{data.length}件はCSVをダウンロードしてください。
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default App;
