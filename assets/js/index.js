import 'babel-core/polyfill';

import { createHistory } from 'history';
import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';
import { ReduxRouter } from 'redux-router';
import bootstrap from 'bootstrap';

import 'bootstrap/less/bootstrap.less'
import '../../less/lierogbg.less';

import App from './containers/App';
import configureStore from './store/configureStore';

const store = configureStore();

render(
  <Provider store={store}>
    <ReduxRouter />
  </Provider>,
  document.getElementById('root')
);
