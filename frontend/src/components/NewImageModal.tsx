import  { useState } from 'react';
import axios from 'axios';

interface NewImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
}

const NewImageModal: React.FC<NewImageModalProps> = ({ isOpen, onClose, onCreated }) => {
  const [clientId, setClientId] = useState("client01");
  const [createdAt, setCreatedAt] = useState("2025-02-24T00:00:00Z");
  const [hardwareId, setHardwareId] = useState("3af9d8da-c689-48f5-bd87-afbfc999e589");
  const [mlTag, setMlTag] = useState("TRAIN");
  const [locationId, setLocationId] = useState("loc1");
  const [userId, setUserId] = useState("user1");
  const [annotationInstrument, setAnnotationInstrument] = useState("instr1");
  const [annotationPolygon, setAnnotationPolygon] = useState('{"points": [[0, 0], [1, 1]]}');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // Parse the polygon field
    let polygon;
    try {
      polygon = JSON.parse(annotationPolygon);
    } catch (err) {
      setError("Invalid JSON in Annotation Polygon");
      setLoading(false);
      return;
    }

    // Build the image form data object
    const imageFormData = {
      image_key: "",
      client_id: clientId,
      created_at: createdAt,
      hardware_id: hardwareId,
      ml_tag: mlTag,
      location_id: locationId,
      user_id: userId,
      annotations: [
        {
          index: 0,
          instrument: annotationInstrument,
          polygon: polygon,
        },
      ],
    };

    // Build FormData to send both the file and JSON string
    const formData = new FormData();
    if (imageFile) {
      formData.append("image_file", imageFile);
    } else {
      setError("Please select an image file");
      setLoading(false);
      return;
    }
    formData.append("image_form", JSON.stringify(imageFormData));

    try {
      await axios.post("http://localhost:8000/images", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onCreated(); 
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      {/* Modal container with fixed header and footer */}
      <div className="bg-white rounded shadow-lg max-w-lg w-full max-h-[700px] flex flex-col">
        {/* Header: Title and optional error */}
        <div className="px-4 py-2 border-b border-gray-200 flex-shrink-0">
          <h2 className="text-2xl font-bold">New Image</h2>
          {error && <p className="text-red-500 mt-2">{error}</p>}
        </div>

        {/* Scrollable Body: Form fields */}
        <div className="px-4 py-2 overflow-auto flex-grow">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium mb-1">Image File</label>
              <label className="block">
                <span className="sr-only">Choose File</span>
                <input
                  type="file"
                  className="block w-full text-sm text-gray-700 
                            file:mr-4 file:py-2 file:px-4
                            file:rounded file:border-0
                            file:text-sm file:font-semibold
                            file:bg-blue-50 file:text-blue-700
                            hover:file:bg-blue-100"
                  onChange={(e) => {
                    if (e.target.files) setImageFile(e.target.files[0]);
                  }}
                />
              </label>
            </div>

            {/* Text fields */}
            <div>
              <label className="block text-sm font-medium">Client ID</label>
              <input
                type="text"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                className="mt-1 block w-full border rounded px-2 py-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Created At</label>
              <input
                type="text"
                value={createdAt}
                onChange={(e) => setCreatedAt(e.target.value)}
                className="mt-1 block w-full border rounded px-2 py-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Hardware ID</label>
              <input
                type="text"
                value={hardwareId}
                onChange={(e) => setHardwareId(e.target.value)}
                className="mt-1 block w-full border rounded px-2 py-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium">ML Tag</label>
              <input
                type="text"
                value={mlTag}
                onChange={(e) => setMlTag(e.target.value)}
                className="mt-1 block w-full border rounded px-2 py-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Location ID</label>
              <input
                type="text"
                value={locationId}
                onChange={(e) => setLocationId(e.target.value)}
                className="mt-1 block w-full border rounded px-2 py-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium">User ID</label>
              <input
                type="text"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className="mt-1 block w-full border rounded px-2 py-1"
              />
            </div>
            {/* Annotation fields */}
            <div>
              <label className="block text-sm font-medium">Annotation Instrument</label>
              <input
                type="text"
                value={annotationInstrument}
                onChange={(e) => setAnnotationInstrument(e.target.value)}
                className="mt-1 block w-full border rounded px-2 py-1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Annotation Polygon (JSON)</label>
              <textarea
                value={annotationPolygon}
                onChange={(e) => setAnnotationPolygon(e.target.value)}
                className="mt-1 block w-full border rounded px-2 py-1"
                rows={3}
              />
            </div>
          </form>
        </div>

        {/* Footer: Action buttons (always visible) */}
        <div className="px-4 py-2 border-t border-gray-200 flex-shrink-0 flex justify-end space-x-4">
          <button
            type="button"
            onClick={onClose}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="" // Optionally, you can associate with the form if you add an id.
            disabled={loading}
            onClick={handleSubmit}
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
          >
            {loading ? "Uploading..." : "Submit"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default NewImageModal;
