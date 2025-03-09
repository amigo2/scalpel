// App.tsx (Main Component simplified)
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { TopBar } from './components/TopBar';
import { ImagesGrid } from './components/ImagesGrid';
import NewImageModal from './components/NewImageModal';
import UpdateImage from './components/UpdateImage';
import NewAnnotationModal from './components/NewAnnotationModal';
import UpdateAnnotationModal from './components/UpdateAnnotationModal';
import { Image } from './types';

function App() {
  const [images, setImages] = useState<Image[]>([]);
  const [isNewImageOpen, setIsNewImageOpen] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");
  const [selectedImageKey, setSelectedImageKey] = useState<string | null>(null);
  const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false);
  const [isAnnotationModalOpen, setIsAnnotationModalOpen] = useState(false);
  const [isUpdateAnnotationModalOpen, setIsUpdateAnnotationModalOpen] = useState(false);

  useEffect(() => {
    axios.get<Image[]>("http://localhost:8000/images")
      .then(response => setImages(response.data));
  }, []);

  const handleDelete = (imageKey: string) => {
    axios.delete(`http://localhost:8000/images/${encodeURIComponent(imageKey)}`)
      .then(() => setImages(prev => prev.filter(img => img.image_key !== imageKey)));
  };

  // Function to trigger the update modal for a specific image
  const handleEdit = (imageKey: string) => {
    setSelectedImageKey(imageKey);
    setIsUpdateModalOpen(true);
  };

  const filteredImages = images.filter(image => {
    const term = searchFilter.toLowerCase();
    return (
      image.location_id?.toLowerCase().includes(term) ||
      image.user_id?.toLowerCase().includes(term) ||
      image.client_id?.toLowerCase().includes(term) ||
      image.annotations.some(ann => ann.instrument.toLowerCase().includes(term))
    );
  });

  return (
    <div className="min-h-screen bg-gray-300">
      <TopBar title="Scalpel" />
      <div className="max-w-screen-lg mx-auto p-6">
        <input
          className="border rounded px-4 py-2 w-full"
          placeholder="Search by location, instrument, or user"
          value={searchFilter}
          onChange={e => setSearchFilter(e.target.value)}
        />
        <button className="mt-4 bg-blue-500 text-white px-4 py-2 rounded" onClick={() => setIsNewImageOpen(true)}>
          New Image
        </button>
        <ImagesGrid
          images={filteredImages}
          onDelete={handleDelete}
          onEdit={key => { setSelectedImageKey(key); setIsUpdateModalOpen(true); }}
          onAddAnnotation={key => { setSelectedImageKey(key); setIsAnnotationModalOpen(true); }}
          onUpdateAnnotation={key => { setSelectedImageKey(key); setIsUpdateAnnotationModalOpen(true); }}
        />
      </div>

      <NewImageModal isOpen={isNewImageOpen} onClose={() => setIsNewImageOpen(false)} />

      {isUpdateModalOpen && selectedImageKey && (
        <UpdateImage imageKey={selectedImageKey} onClose={() => setIsUpdateModalOpen(false)} />
      )}

      {isAnnotationModalOpen && selectedImageKey && (
        <NewAnnotationModal imageKey={selectedImageKey} isOpen={isAnnotationModalOpen} onClose={() => setIsAnnotationModalOpen(false)} />
      )}

      {isUpdateAnnotationModalOpen && selectedImageKey && (
        <UpdateAnnotationModal 
          imageKey={selectedImageKey} 
          isOpen={isUpdateAnnotationModalOpen} 
          onClose={() => setIsUpdateAnnotationModalOpen(false)} 
          annotationIndex={0} 
          initialInstrument="" 
          initialPolygon={{}} 
        />
      )}
    </div>
  );
}

export default App;
