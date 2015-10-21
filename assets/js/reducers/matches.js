import {
  MATCHES_REQUEST, MATCHES_SUCCESS, MATCHES_FAILURE
} from '../actions/matches';

const defaultState = {
  isFetching: false,
  matches: []
};

export default function players(state = defaultState, action) {
  switch (action.type) {
  case MATCHES_REQUEST:
    return Object.assign({}, state, {
      isFetching: true,
    });
  case MATCHES_SUCCESS:
    return Object.assign({}, state, {
      isFetching: false,
      //matches: action.matches
      // FIXME real data
      matches: [{
        player_left: {
          pk: 1,
          name: "poukah",
          color: "#aaaaaa",
          rp_after: 1200,
          rp_change: 5
        },
        player_right: {
          pk: 2,
          name: "etc",
          color: "#222222"
        },
        winner: {
          pk: 1,
          name: "poukah",
          color: "#aaaaaa"
        },
        type: "Ranked",
        start_time: "2014-01-01 18:07",
        rounds: [{
          player_left: {
            pk: 1,
            name: "poukah",
            color: "#aaaaaa",
            lives: 2
          },
          player_right: {
            pk: 2,
            name: "etc",
            color: "#222222",
            lives: 0
          },
          pk: 1,
          map: "pokol2",
          file: "/media/replays/dummy"
        }]
      }]
    });
  case MATCHES_FAILURE:
    // FIXME error handling
    return state;
  default:
    return state;
  }
}
