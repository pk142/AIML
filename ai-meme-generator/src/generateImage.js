const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${API_KEY}`;

export async function generateImage(topic) {
  const response = await fetch(URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [
        {
          parts: [
            {
              text: `Generate a simple, funny meme-style image about: ${topic}. No text or captions baked into the image.`,
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
    throw new Error(`Image generation failed: ${response.status}`);
  }

  const data = await response.json();
  const parts = data.candidates[0].content.parts;
  const imagePart = parts.find((part) => part.inlineData);

  if (!imagePart) {
    throw new Error('No image returned');
  }

  const base64Data = imagePart.inlineData.data;
  return `data:image/png;base64,${base64Data}`;
}