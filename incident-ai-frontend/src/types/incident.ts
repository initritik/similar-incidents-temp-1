// // Typed interfaces document the contract between the frontend and backend.
// // They make API changes easier to detect and help UI code stay predictable as
// // the incident assistant grows.

// export interface SimilarIncident {
//   incident_number: string;
//   short_description: string;
//   description: string;
//   assignment_group: string;
//   priority: string;
//   category: string;
//   resolution_notes: string;
//   similarity_score: number;
// }

// export interface SearchIncidentsRequest {
//   query_text: string;
//   top_k?: number;
// }

// export interface SearchIncidentsResponse {
//   status: string;
//   query_text: string;
//   results: SimilarIncident[];
// }

// export interface ChatRequest {
//   user_query?: string;
//   incident_link?: string;
//   incident_number?: string;
//   top_k?: number;
// }

// export interface ChatResponse {
//   status: string;
//   user_query: string;
//   results: SimilarIncident[];
//   answer: string;
// }





// Typed interfaces document the contract between the frontend and backend.

export interface SimilarIncident {
  incident_number: string;
  short_description: string;
  description: string;
  assignment_group: string;
  priority: string;
  category: string;
  resolution_notes: string;
  /** Direct link to open the incident in the ServiceNow UI. */
  servicenow_link: string;
  similarity_score: number;
}

export interface SearchIncidentsRequest {
  query_text: string;
  top_k?: number;
}

export interface SearchIncidentsResponse {
  status: string;
  query_text: string;
  results: SimilarIncident[];
}

export interface ChatRequest {
  user_query?: string;
  incident_link?: string;
  incident_number?: string;
  top_k?: number;
}

export interface ChatResponse {
  status: string;
  user_query: string;
  results: SimilarIncident[];
  answer: string;
}