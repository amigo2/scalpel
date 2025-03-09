import React, { useState } from 'react';
import axios from 'axios';

interface UpdateImageProps {
  imageKey: string;
  onClose: () => void;
}

const UpdateImage: React.FC<UpdateImageProps> = ({ imageKey, onClose }) => {
  const [scale, setScale] = useState(1.0);
  const [quality, setQuality] = useState(75);
  const [updatedImageUrl, setUpdatedImageUrl] = useState<string>("");
  const [error, setError] = useState("");
  const [dimensions, setDimensions] = useState<{ width: number; height: number } | null>(null);

  const handleUpdate = async () => {
    setError("");
    try {
      // Call the PUT endpoint with the provided scale and quality
      const response = await axios.put(
        `http://localhost:8000/images/${encodeURIComponent(imageKey)}/file`,
        null,
        {
          params: { scale, quality },
          responseType: 'blob'
        }
      );
      // Create an object URL from the returned blob to display the updated image
      const url = URL.createObjectURL(response.data as Blob);
      setUpdatedImageUrl(url);
      // Reset dimensions when a new image is loaded
      setDimensions(null);
    } catch (err: any) {
      console.error("Error updating image:", err);
      setError(err.response?.data?.detail || "An error occurred");
    }
  };

  // Capture the image's natural dimensions when it loads
  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    const { naturalWidth, naturalHeight } = e.currentTarget;
    setDimensions({ width: naturalWidth, height: naturalHeight });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded shadow-lg max-w-lg w-full p-6">
        <h2 className="text-2xl font-bold mb-4">Update Image</h2>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <div className="mt-2">
          <label className="block">
            Scale:
            <input
              type="number"
              step="0.1"
              value={scale}
              onChange={(e) => setScale(parseFloat(e.target.value))}
              className="border rounded px-2 py-1 ml-2"
            />
          </label>
        </div>
        <div className="mt-2">
          <label className="block">
            Quality:
            <input
              type="number"
              value={quality}
              onChange={(e) => setQuality(parseInt(e.target.value))}
              className="border rounded px-2 py-1 ml-2"
            />
          </label>
        </div>
        <button 
          onClick={handleUpdate} 
          className="mt-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
        >
          Update Image
        </button>
        {updatedImageUrl && (
          <div className="mt-4">
            <h4 className="text-md font-semibold">Updated Image Preview:</h4>
            <img 
              src={updatedImageUrl} 
              alt="Updated" 
              className="mt-2 rounded"
              onLoad={handleImageLoad}
            />
            {dimensions && (
              <p className="mt-2 text-sm text-gray-600">
                Dimensions: {dimensions.width} x {dimensions.height} px
              </p>
            )}
          </div>
        )}
        <div className="flex justify-end mt-4">
          <button 
            onClick={onClose} 
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default UpdateImage;
