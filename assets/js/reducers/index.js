import { combineReducers } from 'redux';
import { routerStateReducer as router } from 'redux-router';
import matches from './matches';
import players from './players';

const rootReducer = combineReducers({
  matches,
  players,
  router
});

export default rootReducer;
