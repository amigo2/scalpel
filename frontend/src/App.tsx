import React, { useEffect, useState } from 'react';
import axios from 'axios';
import NewImageModal from './components/NewImageModal';
import UpdateImage from './components/UpdateImage';
import NewAnnotationModal from './components/NewAnnotationModal';
import UpdateAnnotationModal from './components/UpdateAnnotationModal';
import { Image } from './types';
import { TopBar } from './components/TopBar';
import { ImagesGrid } from './components/ImagesGrid';

function App() {
  const [images, setImages] = useState<Image[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");
  const [selectedImageKey, setSelectedImageKey] = useState<string | null>(null);
  const [selectedAnnotationIndex, setSelectedAnnotationIndex] = useState<number | null>(null);
  const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false);
  const [isAnnotationModalOpen, setIsAnnotationModalOpen] = useState(false);
  const [isUpdateAnnotationModalOpen, setIsUpdateAnnotationModalOpen] = useState(false);

  useEffect(() => {
    axios.get<Image[]>("http://localhost:8000/images")
      .then(res => setImages(res.data))
      .catch(err => console.error(err));
  }, []);

  const handleDelete = (imageKey: string) => {
    axios.delete(`http://localhost:8000/images/${encodeURIComponent(imageKey)}`)
      .then(() => setImages(images.filter(img => img.image_key !== imageKey)))
      .catch(err => console.error(err));
  };

  const handleEdit = (imageKey: string) => {
    setSelectedImageKey(imageKey);
    setIsUpdateModalOpen(true);
  };

  const filteredImages = images.filter(img => 
    [img.location_id, img.user_id, img.client_id, ...img.annotations.map(a => a.instrument)]
      .some(val => val?.toLowerCase().includes(searchFilter.toLowerCase()))
  );

  return (
    <div className="min-h-screen bg-gray-300">
      <TopBar title="Scalpel" />
      <div className="max-w-screen-lg mx-auto p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Images</h2>
          <button onClick={() => setIsModalOpen(true)} className="bg-blue-500 text-white px-4 py-2 rounded">
            New Image
          </button>
        </div>
        <input
          type="text"
          placeholder="Search by location, instrument, or user"
          value={searchFilter}
          onChange={(e) => setSearchFilter(e.target.value)}
          className="border rounded w-full p-2 mb-4"
        />
        <ImagesGrid
          images={filteredImages}
          onDelete={handleDelete}
          onEdit={handleEdit}
          onAddAnnotation={(key) => {
            setSelectedImageKey(key);
            setIsAnnotationModalOpen(true);
          }}
          onUpdateAnnotation={(key, idx) => {
            setSelectedImageKey(key);
            setSelectedAnnotationIndex(idx);
            setIsUpdateAnnotationModalOpen(true);
          }}
        />
      </div>

      <NewImageModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
      {isUpdateModalOpen && selectedImageKey && (
        <UpdateImage imageKey={selectedImageKey} onClose={() => setIsUpdateModalOpen(false)} />
      )}
      {isAnnotationModalOpen && selectedImageKey && (
        <NewAnnotationModal
          isOpen={isAnnotationModalOpen}
          imageKey={selectedImageKey}
          onClose={() => setIsAnnotationModalOpen(false)}
        />
      )}

      {isUpdateAnnotationModalOpen && selectedImageKey && selectedAnnotationIndex !== null && (
        <UpdateAnnotationModal
            isOpen={isUpdateAnnotationModalOpen}
            imageKey={selectedImageKey}
            annotationIndex={selectedAnnotationIndex}
            initialInstrument={
            images
                .find(img => img.image_key === selectedImageKey)
                ?.annotations.find(ann => ann.index === selectedAnnotationIndex)?.instrument || ""
            }
            initialPolygon={
            images
                .find(img => img.image_key === selectedImageKey)
                ?.annotations.find(ann => ann.index === selectedAnnotationIndex)?.polygon || {}
            }
            onClose={() => {
            setIsUpdateAnnotationModalOpen(false);
            setSelectedImageKey(null);
            setSelectedAnnotationIndex(null);
            }}
            onUpdated={() => {
            // Optionally refresh images data here after update
            }}
        />
        )}

    </div>
  );
}

export default App;
