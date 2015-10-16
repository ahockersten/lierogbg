import {
  RANKINGS_REQUEST, RANKINGS_SUCCESS, RANKINGS_FAILURE
} from '../actions/rankings';

const defaultState = {
  season: {
    isFetching: false,
    players: []
  },
  alltime: {
    isFetching: false,
    players: []
  }
}

export default function rankings(state = defaultState, action) {
  switch (action.type) {
  case RANKINGS_REQUEST:
    return Object.assign({}, state, {
      [season.isFetching]: true,
      [alltime.isFetching]: true
    });
  case RANKINGS_SUCCESS:
    // FIXME static data for now, read from action.json later
    return {
      season: {
        isFetching: false,
        players: [{
          pk: 1,
          rank: 1,
          name: "poukah",
          color: "ffffff", // FIXME type?
          rp: 1611,
          pp: 0,
          wins: 7,
          losses: 3,
          ties: 0,
          matches: 3,
          lives: 5,
          ante: 52,
          active: true
        }]
      },
      alltime: {
        isFetching: false,
        players: [{
          pk: 1,
          rank: 1,
          name: "poukah",
          color: "ffffff", // FIXME type?
          rp: 1611,
          wins: 56,
          losses: 23,
          ties: 0,
          matches: 22,
          lives: 109,
          ante: 52,
          active: true
        }]
      }
    };
  case RANKINGS_FAILURE:
    // FIXME error handling
    return state;
  default:
    return state;
  }
}
