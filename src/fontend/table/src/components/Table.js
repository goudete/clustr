import React, { useState, useEffect } from 'react';
import { Table, Badge, Menu, Dropdown } from 'antd';
import { DownOutlined } from '@ant-design/icons';
import Description from './Description';
import axios from 'axios';

const menu = (
  <Menu>
    <Menu.Item>Action 1</Menu.Item>
    <Menu.Item>Action 2</Menu.Item>
  </Menu>
);

function NestedTable() {
  const expandedRowRender = () => {
    return <Description/>;
  };

  const setData = useState({});

  const columns = [
    { title: 'Item Name', dataIndex: 'name', key: 'name' },
    { title: 'Price', dataIndex: 'platform', key: 'platform' },
    { title: 'Category', dataIndex: 'version', key: 'version' },
    { title: 'In Stock?', dataIndex: 'upgradeNum', key: 'upgradeNum' },
    // { title: 'Date', dataIndex: 'createdAt', key: 'createdAt' },
    { title: 'Action', key: 'operation', render: () => <a>Publish</a> },
  ];

  // const data = [];
  // for (let i = 0; i < 3; ++i) {
  //   data.push({
  //     key: i,
  //     name: 'Screem',
  //     platform: 'iOS',
  //     version: '10.3.4.5654',
  //     upgradeNum: 500,
  //     creator: 'Jack',
  //     createdAt: '2014-12-24 23:12:00',
  //   });
  // }

  async function fetchData() {
    const res = await fetch('http://localhost:8000/api/');
    res
      .json()
      .then(res => setData(res))
  }

  useEffect(() => {
    fetchData();
  });

  return (
    <Table
      className="components-table-demo-nested"
      columns={columns}
      expandable={{ expandedRowRender }}
      dataSource={setData}
    />
  );
}

export default NestedTable;
