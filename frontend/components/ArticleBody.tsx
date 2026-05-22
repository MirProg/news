export default function ArticleBody({ html }: { html: string }) {
  return (
    <div
      className="article-body prose prose-invert max-w-none"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
