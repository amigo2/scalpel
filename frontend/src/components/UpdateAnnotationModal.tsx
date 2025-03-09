// components/UpdateAnnotationModal.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface UpdateAnnotationModalProps {
  isOpen: boolean;
  imageKey: string;
  annotationIndex: number;
  initialInstrument: string;
  initialPolygon: Record<string, unknown>;
  onClose: () => void;
  onUpdated?: () => void;
}

const UpdateAnnotationModal: React.FC<UpdateAnnotationModalProps> = ({
  isOpen,
  imageKey,
  annotationIndex,
  initialInstrument,
  initialPolygon,
  onClose,
  onUpdated,
}) => {
  const [instrument, setInstrument] = useState(initialInstrument);
  const [polygon, setPolygon] = useState(JSON.stringify(initialPolygon, null, 2));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setInstrument(initialInstrument);
    setPolygon(JSON.stringify(initialPolygon, null, 2));
  }, [initialInstrument, initialPolygon, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    let polygonJson;
    try {
      polygonJson = JSON.parse(polygon);
    } catch {
      setError("Invalid JSON format in Polygon field.");
      setLoading(false);
      return;
    }

    const sanitizedImageKey = imageKey.startsWith('/') ? imageKey.substring(1) : imageKey;

    try {
      await axios.put(
        `http://localhost:8000/images/${encodeURIComponent(sanitizedImageKey)}/annotations/${annotationIndex}`,
        { instrument, polygon: polygonJson }
      );

      onUpdated?.();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred while updating.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
        <h2 className="text-xl font-semibold mb-4">Update Annotation</h2>

        {error && <div className="text-red-500 mb-3">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="block font-medium">Instrument</label>
            <input
              type="text"
              value={instrument}
              onChange={(e) => setInstrument(e.target.value)}
              className="border rounded px-2 py-1 w-full mt-1"
              required
            />
          </div>

          <div className="mb-3">
            <label className="block font-medium">Polygon (JSON)</label>
            <textarea
              value={polygon}
              onChange={(e) => setPolygon(e.target.value)}
              className="border rounded px-2 py-1 w-full mt-1 font-mono text-sm"
              rows={5}
              required
            />
          </div>

          <div className="mt-5 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded"
            >
              {loading ? "Updating..." : "Update"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UpdateAnnotationModal;
