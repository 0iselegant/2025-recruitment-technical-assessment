// use axum::{http::StatusCode, response::IntoResponse, Json};
// use serde::{Deserialize, Serialize};

// pub async fn process_data(Json(request): Json<DataRequest>) -> impl IntoResponse {
//     // Calculate sums and return response

//     let response = DataResponse {
        
//     };

//     (StatusCode::OK, Json(response))
// }

// #[derive(Deserialize)]
// pub struct DataRequest {
//     // Add any fields here
// }

// #[derive(Serialize)]
// pub struct DataResponse {
//     // Add any fields here
// }

use axum::{http::StatusCode, response::IntoResponse, Json};
use serde::{Deserialize, Serialize};
use serde_json::Number;

pub async fn process_data(Json(request): Json<DataRequest>) -> impl IntoResponse {
    // Calculate the number of characters in the strings
    let total_string_length = request.data.iter()
        .filter_map(|item| match item {
            // Check if item is a string and get its length
            Value::String(s) => Some(s.len()),
            _ => None,
        })
        .sum::<usize>();

    // Calculate the sum of the integers
    let sum_of_integers = request.data.iter()
        .filter_map(|item| match item {
            // Check if item is an integer and sum them
            Value::Number(n) => n.as_u64(),
            _ => None,
        })
        .sum::<u64>();

    // Create the response with the new field names
    let response = DataResponse {
        string_len: total_string_length,
        int_sum: sum_of_integers,
    };

    (StatusCode::OK, Json(response)) // Return response as JSON
}

#[derive(Deserialize)]
pub struct DataRequest {
    pub data: Vec<Value>,
}

#[derive(Serialize)]
pub struct DataResponse {
    #[serde(rename = "string_len")] // Rename field to "string_len"
    pub string_len: usize,

    #[serde(rename = "int_sum")] // Rename field to "int_sum"
    pub int_sum: u64,
}

// Enum to represent the possible types in the data (strings or numbers)
#[derive(Deserialize, Serialize)]
#[serde(untagged)]
pub enum Value {
    String(String),
    Number(Number),
}