import React, { Component, PropTypes } from 'react';

export class TableHeader extends Component {
  render() {
    const { name, sortBy, sortOrder, sorter, cssClasses,
            changeSorting } = this.props;
    let classes;
    let sortSymbol = "";
    if (sorter == sortBy) {
      classes = _.reduce(cssClasses,
                         (acc, n) => acc + ', ' + n, 'sorter');
      sortSymbol = sortOrder == 'asc' ? '▼' : '▲';
    }
    else {
      classes = _.reduce(cssClasses,
                         (acc, n) => acc + ', ' + n, '');
    }
    return (
      <th className={classes}
          onClick={changeSorting.bind(null, sorter)}>
        {name} {sortSymbol}
      </th>
    );
  }
}

TableHeader.propTypes = {
  // the externally visible name to put on this header
  name: PropTypes.string.isRequired,
  // additional css classes for this
  cssClasses: PropTypes.arrayOf(PropTypes.string),
  // the player property to use for sorting
  sorter: PropTypes.string.isRequired,
  // the player property currently being used for sorting
  sortBy: PropTypes.string.isRequired,
  // the current sorting order, 'asc' or 'desc'
  sortOrder: PropTypes.string.isRequired,
  // function to call to change the sorting
  changeSorting: PropTypes.func.isRequired
};
TableHeader.defaultProps = {
  cssClasses: []
};

export default TableHeader;
