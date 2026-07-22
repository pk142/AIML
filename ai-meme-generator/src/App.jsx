import { useState } from 'react';
import MemeCard from './MemeCard';
import { generateCaption } from './generateCaption';
//import { generateImage } from './generateImage';
import './App.css';

function App() {
  const [topic, setTopic] = useState('');
  const [caption, setCaption] = useState('When your code finally runs on the first try');
  //const [imageUrl, setImageUrl] = useState('https://picsum.photos/300/300');
  const [isLoading, setIsLoading] = useState(false);

  async function handleGenerate() {
    if (!topic.trim()) return;
    setIsLoading(true);
    try {
      const newCaption = await generateCaption(topic);
      setCaption(newCaption);
    } catch (error) {
      console.error('Failed to generate caption:', error);
      setCaption('Oops — something went wrong. Try again.');
    } finally {
      setIsLoading(false);
    }
    /*setIsLoading(true);
    try {
      const [newCaption, newImage] = await Promise.all([
        generateCaption(topic),
        generateImage(topic),
      ]);
      setCaption(newCaption);
      setImageUrl(newImage);
    } catch (error) {
      console.error('Failed to generate meme:', error);
      setCaption('Oops — something went wrong. Try again.');
    } finally {
      setIsLoading(false);
    }*/
  }

  return (
    <div className="app">
      <h1>AI Meme Generator</h1>
      <h2>Generate a Meme based on a Topic</h2>

      <input
        type="text"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Enter a topic (e.g. Mondays, debugging, cats)..."
        style={{ width: '300px', padding: '8px', marginRight: '8px' }}
      />

      <button onClick={handleGenerate} disabled={isLoading || !topic.trim()}>
        {isLoading ? 'Generating...' : 'Generate Caption'}
      </button>

      <div style={{ marginTop: '16px' }}>
        <MemeCard
          imageUrl="https://picsum.photos/300/300"
          caption={caption}
        />  
       {/* <MemeCard imageUrl={imageUrl} caption={caption} /> */} 
      </div>
    </div>
  );
}

export default App;