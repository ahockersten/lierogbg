import fetch from 'isomorphic-fetch';

export const PLAYERS_REQUEST = 'PLAYERS_REQUEST';
export const PLAYERS_SUCCESS = 'PLAYERS_SUCCESS';
export const PLAYERS_FAILURE = 'PLAYERS_FAILURE';

// called to request an updated list of players
function playersRequest() {
  return {
    type: PLAYERS_REQUEST
  };
}

// called when the server returns a list of players
function playersSuccess(json) {
  return {
    type: PLAYERS_SUCCESS,
    players: json
  };
}

// called on failure to get players
function playersFailure(err) {
  return {
    type: PLAYERS_FAILURE,
    err: err
  };
}

export function fetchPlayers() {
  // FIXME error handling
  return function(dispatch) {
    return fetch('/api/rankings')
      .then(response => response.json())
      .then(json =>
        dispatch(playersSuccess(json))
    );
  };
}

