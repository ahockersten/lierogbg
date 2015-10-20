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
    // this is kept so that when I write tests later, I can reuse it.
    /*return {
      isFetching: false,
      players: [{
        pk: 1,
        name: "poukah",
        color: "#ffffff",
        ante: 52,
        active: true,
        season: {
          rank: 1,
          rp: 1611,
          pp: 0,
          wins: 7,
          losses: 3,
          ties: 0,
          matches: 3,
          lives: 5,
        },
        allTime: {
          rank: 1,
          rp: 1611,
          pp: 0,
          wins: 56,
          losses: 23,
          ties: 0,
          matches: 22,
          lives: 109,
        }
      },{
        pk: 2,
        name: "joosef",
        color: "#aaaaaa",
        ante: 10,
        active: true,
        season: {
          rank: 2,
          rp: 1011,
          pp: 20,
          wins: 7,
          losses: 5,
          ties: 0,
          matches: 3,
          lives: -5,
        },
        allTime: {
          rank: 2,
          rp: 1011,
          pp: 20,
          wins: 5,
          losses: 5,
          ties: 0,
          matches: 2,
          lives: -9,
        }
      },{
        pk: 3,
        name: "maria",
        color: "#cccccc",
        ante: 10,
        active: false,
        season: {
          rank: 3,
          rp: 1001,
          pp: 20,
          wins: 7,
          losses: 3,
          ties: 0,
          matches: 3,
          lives: -5,
        },
        allTime: {
          rank: 3,
          rp: 1001,
          pp: 20,
          wins: 5,
          losses: 2,
          ties: 0,
          matches: 2,
          lives: -9,
        }
      }]
    };*/
  case PLAYERS_FAILURE:
    // FIXME error handling
    return state;
  default:
    return state;
  }
}
