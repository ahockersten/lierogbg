export const PLAYERS_REQUEST = 'PLAYERS_REQUEST';
export const PLAYERS_SUCCESS = 'PLAYERS_SUCCESS';
export const PLAYERS_FAILURE = 'PLAYERS_FAILURE';

// called to request an updated list of players
export function playersRequest() {
  return {
    type: PLAYERS_REQUEST
  };
}

// called when the server returns a list of players
export function playersSuccess(json) {
  return {
    type: PLAYERS_SUCCESS,
    players: json.data
  };
}

// called on failure to get players
export function playersFailure(err) {
  return {
    type: PLAYERS_FAILURE,
    err: err
  };
}

export function fetchPlayers() {
  // FIXME fetch actual data
  return playersSuccess({});
}
