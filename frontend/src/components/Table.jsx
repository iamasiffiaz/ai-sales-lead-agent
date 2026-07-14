export default function Table({ columns, rows, empty = 'No records found.' }) {
  if (!rows?.length) {
    return <p className="py-10 text-center text-sm text-ink-500">{empty}</p>;
  }
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-left text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-ink-500">
            {columns.map((col) => (
              <th key={col.key} className="whitespace-nowrap px-3 py-3 font-semibold">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={row.id || idx} className="border-b border-slate-100 hover:bg-slate-50/80">
              {columns.map((col) => (
                <td key={col.key} className="px-3 py-3 align-middle text-ink-800">
                  {col.render ? col.render(row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
