import React, { useEffect, useState } from 'react';

interface Annotation {
  index: number;
  instrument: string;
  polygon?: Record<string, unknown>;
}

interface Image {
  image_key: string;
  client_id: string;
  created_at: string;
  hardware_id: string;
  ml_tag?: string;
  location_id?: string;
  user_id?: string;
  annotations: Annotation[];
}

function App() {
  const [images, setImages] = useState<Image[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/images')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then((data: Image[]) => setImages(data))
      .catch((error) => console.error('Error fetching images:', error));
  }, []);

  return (
    <div>
      <h1>Images</h1>
      <ul>
        {images.map((image) => (
          <li key={image.image_key}>
            <strong>Image:</strong> {image.image_key} <br />
            <strong>Client:</strong> {image.client_id} <br />
            <strong>Created at:</strong> {image.created_at} <br />
            <strong>Hardware:</strong> {image.hardware_id} <br />
            {/* Display the image using the backend URL */}
            <img 
              src={`http://localhost:8000${image.image_key}`} 
              alt="Uploaded" 
              style={{ maxWidth: '300px', marginTop: '10px' }}
            />

            {/* <img
              src={`http://localhost:8000${image.image_key}`}
              alt="Uploaded"
              style={{ maxWidth: '300px', marginTop: '10px' }}
            /> */}
            {image.annotations.length > 0 && (
              <ul>
                {image.annotations.map((ann) => (
                  <li key={ann.index}>
                    <strong>Instrument:</strong> {ann.instrument} <br />
                    <strong>Polygon:</strong> {JSON.stringify(ann.polygon)}
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
