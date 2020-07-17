import { Descriptions } from 'antd';
import React from 'react';
import { Row, Col } from 'antd';
import Avatar from './UploadSquare';
function Description() {
  return (
    <Descriptions title="Item Name Here">
      <Descriptions.Item label="Description">Hangzhou, Zhejiang</Descriptions.Item>
      <Descriptions.Item label="Image">
      </Descriptions.Item>
      <Descriptions.Item>
      </Descriptions.Item>
      <Descriptions.Item>
      <Avatar/>
      </Descriptions.Item>
    </Descriptions>
  )
}

export default Description;
