import { useState } from 'react';
import axios from 'axios';

interface UpdateImageProps {
  imageKey: string;
  onClose: () => void;
}

const UpdateImage: React.FC<UpdateImageProps> = ({ imageKey, onClose }) => {
  const [scale, setScale] = useState(1.0);
  const [quality, setQuality] = useState(75);
  const [imageUrl, setImageUrl] = useState(`http://localhost:8000${imageKey}`);
  const [dimensions, setDimensions] = useState<{ width: number; height: number } | null>(null);
  const [error, setError] = useState("");

  const updateImage = async () => {
    setError("");
    try {
      const response = await axios.put(
        `http://localhost:8000/images/${encodeURIComponent(imageKey)}/file`,
        null,
        {
          params: { scale, quality },
          responseType: 'blob',
        }
      );
      const updatedUrl = URL.createObjectURL(response.data as Blob);
      setImageUrl(updatedUrl);
      setDimensions(null); // Reset dimensions so new image dimensions are updated correctly
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred");
    }
  };

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const { naturalWidth, naturalHeight } = e.currentTarget;
    setDimensions({ width: naturalWidth, height: naturalHeight });
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded shadow-lg max-w-lg w-full p-6">
        <h2 className="text-2xl font-bold mb-4">Update Image</h2>
        <p className="text-sm text-gray-600 mb-4">
          Update the scale and quality(only JPEG) of the image.  
          The updated image will replace the preview below.
        </p>
        {error && <p className="text-red-500 mb-4">{error}</p>}

        <img
          src={imageUrl}
          alt="Current"
          className="rounded mb-2"
          onLoad={handleImageLoad}
        />
        {dimensions && (
          <p className="text-sm text-gray-500 mb-4">
            Dimensions: {dimensions.width}px × {dimensions.height}px
          </p>
        )}

        <div className="mb-2">
          <label>
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
        <div className="mb-4">
          <label>
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
          onClick={updateImage}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Update Image
        </button>

        <div className="flex justify-end mt-4">
          <button
            onClick={onClose}
            className="bg-gray-500 text-white px-4 py-2 rounded"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default UpdateImage;
