export const RANKINGS_REQUEST = 'RANKINGS_REQUEST';
export const RANKINGS_SUCCESS = 'RANKINGS_SUCCESS';
export const RANKINGS_FAILURE = 'RANKINGS_FAILURE';

// called to request an updated list of rankings
export function rankingsRequest() {
  return {
    type: RANKINGS_REQUEST
  };
}

// called when the server returns a list of rankings
export function rankingsSuccess(json) {
  return {
    type: RANKINGS_SUCCESS,
    rankings: json.data
  };
}

// called on failure to get rankings
export function rankingsFailure(err) {
  return {
    type: RANKINGS_FAILURE,
    err: err
  };
}

export function fetchRankings() {
  // FIXME fetch actual data
  return rankingsSuccess({});
}
