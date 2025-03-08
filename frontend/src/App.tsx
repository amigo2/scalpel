import React, { useEffect, useState } from 'react';
import axios from 'axios';

// Types
interface Annotation {
  index: number;
  instrument: string;
  polygon?: Record<string, unknown>;
}

export interface Image {
  image_key: string;
  client_id: string;
  created_at: string;
  hardware_id: string;
  ml_tag?: string;
  location_id?: string;
  user_id?: string;
  annotations: Annotation[];
}

// TopBar Component
const TopBar: React.FC<{ title: string }> = ({ title }) => {
  return (
    <div style={{
      background: '#333',
      color: '#fff',
      padding: '10px 20px'
    }}>
      <h1 style={{ margin: 0 }}>{title}</h1>
    </div>
  );
};

// ImageCard Component
const ImageCard: React.FC<{ image: Image }> = ({ image }) => {
  return (
    <div style={{
      border: '1px solid #ddd',
      borderRadius: '8px',
      padding: '10px',
      margin: '10px',
      background: '#fff'
    }}>
      <img 
        src={`http://localhost:8000${image.image_key}`} 
        alt="Uploaded" 
        style={{
          width: '100%',
          height: 'auto',
          borderRadius: '4px'
        }}
      />
      <div style={{ marginTop: '10px' }}>
        <p><strong>Client:</strong> {image.client_id}</p>
        <p><strong>Created at:</strong> {image.created_at}</p>
        <p><strong>Hardware:</strong> {image.hardware_id}</p>
      </div>
    </div>
  );
};

// ImagesGrid Component (2 columns)
const ImagesGrid: React.FC<{ images: Image[] }> = ({ images }) => {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(2, 1fr)',
      gap: '20px',
      padding: '20px'
    }}>
      {images.map(image => (
        <ImageCard key={image.image_key} image={image} />
      ))}
    </div>
  );
};

// Main App Component
function App() {
  const [images, setImages] = useState<Image[]>([]);

  useEffect(() => {
    axios.get<Image[]>('http://localhost:8000/images')
      .then((response) => {
        setImages(response.data);
      })
      .catch((error) => {
        console.error('Error fetching images:', error);
      });
  }, []);

  return (
    <div>
      <TopBar title="Scalpel" />
      <h2 style={{ padding: '20px' }}>Images</h2>
      <ImagesGrid images={images} />
    </div>
  );
}

export default App;
