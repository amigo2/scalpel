export interface Annotation {
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
  