import { combineReducers } from 'redux';
import { routerStateReducer as router } from 'redux-router';
import rankings from './rankings';

const rootReducer = combineReducers({
  rankings,
  router
});

export default rootReducer;
