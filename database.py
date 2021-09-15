from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class PostType(Base):
    __tablename__ = 'post_type'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(30), nullable=False, unique=True)


class Post(Base):
    __tablename__ = 'post'
    id = Column('id', Integer, primary_key=True)
    type = Column('post_type_id', Integer, ForeignKey('post_type.id'))
    author = Column('author', String(30), nullable=False)
    upload_at = Column('upload_at', DateTime, nullable=False)
    title = Column('title', String(100), nullable=False)
    content = Column('content', Text, nullable=False)
    attachedFiles = relationship('AttachedFile', cascade='all, delete')


class AttachedFile(Base):
    __tablename__ = 'attached_file'
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    post = Column('post_id', Integer, ForeignKey('post.id'))
    attachedFileId = Column('attached_file_id', String(30), nullable=False)
    fileSn = Column('file_sn', Integer, nullable=False)
    name = Column('name', String(255), nullable=False)
    size = Column('size', Integer, nullable=False)
    downloadUrl = Column('download_url', String(255), nullable=False)
    previewUrl = Column('preview_url', String(255), nullable=False)
