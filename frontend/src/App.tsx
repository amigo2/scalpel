import React, { useEffect, useState } from 'react';
import axios from 'axios';
import NewImageModal from './components/NewImageModal';

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

// TopBar Component (full width)
const TopBar: React.FC<{ title: string }> = ({ title }) => {
  return (
    <div className="w-full bg-gray-800 text-white p-4">
      <h1 className="text-2xl font-bold text-center">{title}</h1>
    </div>
  );
};

// ImageCard Component (single column)
const ImageCard: React.FC<{ image: Image; onDelete: (imageKey: string) => void }> = ({ image, onDelete }) => {
  return (
    <div className="bg-white shadow rounded p-4 max-w-xs mx-auto flex flex-col">
      <img 
        src={`http://localhost:8000${image.image_key}`} 
        alt="Uploaded" 
        className="w-full h-auto rounded"
      />
      <div className="mt-4 space-y-1">
        <p 
          className="text-sm overflow-hidden whitespace-nowrap text-ellipsis" 
          title={image.image_key}
        >
          <span className="font-semibold">Image Key:</span> {image.image_key}
        </p>
        <p className="text-sm">
          <span className="font-semibold">Client:</span> {image.client_id}
        </p>
        <p className="text-sm">
          <span className="font-semibold">Created at:</span> {image.created_at}
        </p>
        <p className="text-sm">
          <span className="font-semibold">Hardware:</span> {image.hardware_id}
        </p>
        <p className="text-sm">
          <span className="font-semibold">ML Tag:</span> {image.ml_tag}
        </p>
        <p className="text-sm">
          <span className="font-semibold">Location:</span> {image.location_id}
        </p>
        <p className="text-sm">
          <span className="font-semibold">User:</span> {image.user_id}
        </p>
        {image.annotations && image.annotations.length > 0 && (
          <div className="mt-2">
            <p className="text-sm font-semibold">Annotations:</p>
            {image.annotations.map((ann, idx) => (
              <div key={idx} className="pl-2 border-l border-gray-300">
                <p className="text-sm">
                  <span className="font-semibold">Index:</span> {ann.index}
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Instrument:</span> {ann.instrument}
                </p>
                <p className="text-sm">
                  <span className="font-semibold">Polygon:</span> {JSON.stringify(ann.polygon)}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
      <div className="mt-auto pt-4 flex justify-between w-full">
        <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">
          Edit
        </button>
        <button 
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
          onClick={() => onDelete(image.image_key)}
        >
          Delete
        </button>
      </div>
    </div>
  );
};

// ImagesGrid Component (4 columns)
const ImagesGrid: React.FC<{ images: Image[]; onDelete: (imageKey: string) => void }> = ({ images, onDelete }) => {
  return (
    <div className="grid grid-cols-3 gap-6 p-6">
      {images.map((image) => (
        <ImageCard key={image.image_key} image={image} onDelete={onDelete} />
      ))}
    </div>
  );
};

// Main App Component with search functionality
function App() {
  const [images, setImages] = useState<Image[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");

  useEffect(() => {
    axios.get<Image[]>("http://localhost:8000/images")
      .then((response) => {
        setImages(response.data);
      })
      .catch((error) => {
        console.error('Error fetching images:', error);
      });
  }, []);

  // Function to delete an image by calling the DELETE endpoint
  const handleDelete = (imageKey: string) => {
    // Encode the imageKey to ensure special characters (like slashes) are handled correctly
    axios.delete(`http://localhost:8000/images/${encodeURIComponent(imageKey)}`)
      .then((response) => {
        // Filter out the deleted image from state
        setImages((prevImages) => prevImages.filter((img) => img.image_key !== imageKey));
      })
      .catch((error) => {
        console.error('Error deleting image:', error);
      });
  };

  // Filter images based on location, instrument, user, or client (case-insensitive)
  const filteredImages = images.filter((image) => {
    if (!searchFilter) return true;
    const searchTerm = searchFilter.toLowerCase();
    const locationMatch = image.location_id && image.location_id.toLowerCase().includes(searchTerm);
    const instrumentMatch =
      image.annotations &&
      image.annotations.some(ann => ann.instrument.toLowerCase().includes(searchTerm));
    const userMatch = image.user_id && image.user_id.toLowerCase().includes(searchTerm);
    const clientMatch = image.client_id && image.client_id.toLowerCase().includes(searchTerm);
    return locationMatch || instrumentMatch || userMatch || clientMatch;
  });

  return (
    <div className="min-h-screen bg-gray-300">
      <TopBar title="Scalpel" />
      <div className="max-w-screen-lg mx-auto">
        {/* Header Bar with Title, New Image Button, and Combined Search Bar */}
        <div className="flex flex-col p-6 bg-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Images</h2>
            <button
              onClick={() => setIsModalOpen(true)}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
            >
              New Image
            </button>
          </div>
          <div>
            <input 
              type="text"
              placeholder="Search by location, instrument, or user"
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="px-4 py-2 border rounded w-full"
            />
          </div>
        </div>
        <ImagesGrid images={filteredImages} onDelete={handleDelete} />
      </div>
      <NewImageModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}

export default App;
