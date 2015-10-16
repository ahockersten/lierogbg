import { combineReducers } from 'redux';
import { routerStateReducer as router } from 'redux-router';
import counter from './counter';

const rootReducer = combineReducers({
  counter,
  router
});

export default rootReducer;
