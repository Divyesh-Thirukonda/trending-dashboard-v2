import { dynamo } from '@/lib/dynamo';
import { GetCommand } from "@aws-sdk/lib-dynamodb";
import {
  Youtube,
  MessageCircle,
  Search,
  BookOpen,
  Terminal,
  Github,
  ExternalLink
} from 'lucide-react';

// Types corresponding to JSON structure
type TrendItem = {
  title?: string;
  name?: string;
  views?: string | number;
  channel?: string;
  score?: number;
  stars?: number;
  description?: string;
  url?: string;
  rank?: number;
}

export const revalidate = 60; // Revalidate every minute

async function getTrends(source: string): Promise<TrendItem[]> {
  try {
    const { Item } = await dynamo.send(new GetCommand({
      TableName: "TrendingData",
      Key: { source }
    }));
    return (Item?.data as TrendItem[]) || [];
  } catch (e) {
    console.error(`Error fetching ${source}:`, e);
    return [];
  }
}

export default async function Home() {
  const [youtube, tiktok, google, wiki, hn, github] = await Promise.all([
    getTrends('youtube'),
    getTrends('tiktok'),
    getTrends('google_trends'),
    getTrends('wikipedia'),
    getTrends('hackernews'),
    getTrends('github')
  ]);

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100 p-6 md:p-12 font-sans">
      <header className="mb-12 text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-orange-400 to-amber-400 bg-clip-text text-transparent mb-4">
          Trending Pulse (AWS)
        </h1>
        <p className="text-neutral-400">Real-time insights. Powered by DynamoDB.</p>
      </header>

      <div className="max-w-7xl mx-auto space-y-12">

        {/* Social Section */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <MessageCircle className="w-6 h-6 text-indigo-400" />
            <h2 className="text-2xl font-bold tracking-tight">Social Media</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

            {/* YouTube */}
            <Card title="YouTube Trending" icon={<Youtube className="text-red-500" />}>
              {youtube.slice(0, 8).map((v: any, i: number) => (
                <div key={i} className="flex flex-col gap-1 py-3 border-b border-neutral-800 last:border-0">
                  <span className="font-medium text-sm line-clamp-2">{v.title}</span>
                  <div className="flex justify-between text-xs text-neutral-500">
                    <span>{v.channel}</span>
                    <span>{v.views} views</span>
                  </div>
                </div>
              ))}
              {youtube.length === 0 && <EmptyState />}
            </Card>

            {/* TikTok */}
            <Card title="TikTok Viral" icon={<MessageCircle className="text-cyan-400" />}>
              {tiktok.slice(0, 8).map((t: any, i: number) => (
                <div key={i} className="flex items-center justify-between py-3 border-b border-neutral-800 last:border-0">
                  <div className="flex items-center gap-3">
                    <span className="text-neutral-500 font-mono text-xs">#{t.rank || i + 1}</span>
                    <span className="font-bold text-sm bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                      {t.name}
                    </span>
                  </div>
                  <span className="text-xs text-neutral-500 font-mono">{t.views}</span>
                </div>
              ))}
              {tiktok.length === 0 && <EmptyState />}
            </Card>

            {/* Google */}
            <Card title="Google Searches" icon={<Search className="text-blue-500" />}>
              {google.map((g: any, i: number) => (
                <div key={i} className="flex items-center gap-3 py-3 border-b border-neutral-800 last:border-0">
                  <span className="text-neutral-500 font-mono text-xs">{i + 1}</span>
                  <span className="font-medium text-sm">{g.name}</span>
                </div>
              ))}
              {google.length === 0 && <EmptyState />}
            </Card>

          </div>
        </section>

        {/* Tech Section */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <Terminal className="w-6 h-6 text-green-400" />
            <h2 className="text-2xl font-bold tracking-tight">Tech & Knowledge</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

            {/* Wiki */}
            <Card title="Wikipedia Top Reads" icon={<BookOpen className="text-white" />}>
              {wiki.length > 0 ? wiki.slice(0, 10).map((w: any, i: number) => (
                <div key={i} className="flex justify-between items-center py-2.5 border-b border-neutral-800 last:border-0">
                  <div className="flex items-center gap-3 overflow-hidden">
                    <span className="text-neutral-600 font-mono text-xs min-w-[20px]">#{i + 1}</span>
                    <span className="text-sm truncate">{w.title}</span>
                  </div>
                  <span className="text-xs text-neutral-500">{w.views}</span>
                </div>
              )) : <EmptyState />}
            </Card>

            {/* Hacker News */}
            <Card title="Hacker News" icon={<Terminal className="text-orange-500" />}>
              {hn.length > 0 ? hn.map((h: any, i: number) => (
                <div key={i} className="py-2.5 border-b border-neutral-800 last:border-0">
                  <a href={h.url} target="_blank" className="text-sm hover:text-orange-400 transition-colors line-clamp-2 mb-1 block">
                    {h.title}
                  </a>
                  <div className="flex items-center gap-2 text-xs text-neutral-500">
                    <span className="text-orange-500/80">{h.score} pts</span>
                    <span>•</span>
                    <ExternalLink className="w-3 h-3" />
                  </div>
                </div>
              )) : <EmptyState />}
            </Card>

            {/* GitHub */}
            <Card title="GitHub Trending" icon={<Github className="text-purple-400" />}>
              {github.length > 0 ? github.map((r: any, i: number) => (
                <div key={i} className="py-3 border-b border-neutral-800 last:border-0">
                  <div className="flex items-center justify-between mb-1">
                    <a href={r.url} target="_blank" className="font-bold text-sm text-blue-400 hover:underline truncate max-w-[200px]">
                      {r.name}
                    </a>
                    <div className="flex items-center gap-1 text-xs text-neutral-400">
                      <span className="text-yellow-500">★</span>
                      {r.stars}
                    </div>
                  </div>
                  <p className="text-xs text-neutral-500 line-clamp-2">{r.description}</p>
                </div>
              )) : <EmptyState />}
            </Card>

          </div>
        </section>

      </div>
    </main>
  );
}

function Card({ title, icon, children }: { title: string, icon: React.ReactNode, children: React.ReactNode }) {
  return (
    <div className="bg-neutral-900/50 backdrop-blur-md border border-white/5 rounded-xl overflow-hidden shadow-2xl hover:border-white/10 transition-colors">
      <div className="p-4 border-b border-white/5 flex items-center gap-3 bg-white/5">
        {icon}
        <h3 className="font-semibold text-neutral-200">{title}</h3>
      </div>
      <div className="p-4 h-[400px] overflow-y-auto scrollbar-thin scrollbar-thumb-neutral-800 scrollbar-track-transparent">
        {children}
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="h-full flex flex-col items-center justify-center text-neutral-600 space-y-2">
      <div className="animate-spin w-6 h-6 border-2 border-neutral-700 border-t-neutral-500 rounded-full"></div>
      <span className="text-sm">Connecting to DynamoDB...</span>
    </div>
  )
}
