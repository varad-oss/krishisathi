'use client';

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

/** Daily counts. Loaded lazily; the page also renders the same numbers as an accessible table. */
export default function TrendChart({ data, formatDate, formatNumber }: { data: { date: string; count: number }[]; formatDate: (d: string) => string; formatNumber: (n: number) => string }) {
  return (
    <div className="h-56 w-full" aria-hidden>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e3e1d6" />
          <XAxis dataKey="date" tickFormatter={formatDate} tick={{ fontSize: 11, fill: '#6f7d73' }} axisLine={false} tickLine={false} minTickGap={16} />
          <YAxis allowDecimals={false} tickFormatter={formatNumber} tick={{ fontSize: 11, fill: '#6f7d73' }} axisLine={false} tickLine={false} />
          <Tooltip labelFormatter={(d) => formatDate(String(d))} formatter={(v) => formatNumber(Number(v))} cursor={{ fill: '#eef5ec' }} />
          <Bar dataKey="count" fill="#2f6b3f" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
