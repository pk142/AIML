const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key=${API_KEY}`;

export async function generateCaption(topic) {
  const response = await fetch(URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [
        {
          parts: [
            {
              text: `Write one short, funny meme caption about: ${topic}. Just the caption text, no quotes, no explanation.`,
            },
          ],
        },
      ],
    }),
  });

  if (!response.ok) {
    if (response.status === 429) {
      throw new Error('Rate limit hit — wait a minute before trying again.');
    }
    throw new Error(`Caption generation failed: ${response.status}`);
  }

  const data = await response.json();
  const caption = data.candidates[0].content.parts[0].text.trim();
  return caption;
}