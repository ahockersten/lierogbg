import {
  PLAYERS_REQUEST, PLAYERS_SUCCESS, PLAYERS_FAILURE
} from '../actions/players';

const defaultState = {
  isFetching: false,
  players: []
};

export default function players(state = defaultState, action) {
  switch (action.type) {
  case PLAYERS_REQUEST:
    return Object.assign({}, state, {
      isFetching: true,
    });
  case PLAYERS_SUCCESS:
    return Object.assign({}, state, {
      isFetching: false,
      players: action.players
    });
  case PLAYERS_FAILURE:
    // FIXME error handling
    return state;
  default:
    return state;
  }
}
