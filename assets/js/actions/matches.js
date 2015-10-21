import fetch from 'isomorphic-fetch';

export const MATCHES_REQUEST = 'MATCHES_REQUEST';
export const MATCHES_SUCCESS = 'MATCHES_SUCCESS';
export const MATCHES_FAILURE = 'MATCHES_FAILURE';

// called to request an updated list of matches
function matchesRequest() {
  return {
    type: MATCHES_REQUEST
  };
}

// called when the server returns a list of matches
function matchesSuccess(json) {
  return {
    type: MATCHES_SUCCESS,
    matches: json
  };
}

// called on failure to get players
function matchesFailure(err) {
  return {
    type: MATCHES_FAILURE,
    err: err
  };
}

export function fetchMatches() {
  // FIXME error handling
  // FIXME load data from server
  return matchesSuccess({});
  /*return dispatch => {
    dispatch(matchesRequest());
    return fetch('/api/matches')
      .then(response => response.json())
      .then(json =>
        dispatch(matchesSuccess(json))
    );
  };*/
}

