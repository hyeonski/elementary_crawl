import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { EntityNotFoundError, Repository } from 'typeorm';
import { PostType } from './entities/post-type.entity';
import { Post } from './entities/post.entity';

@Injectable()
export class AppService {
  constructor(
    @InjectRepository(Post) private readonly postRepository: Repository<Post>,
    @InjectRepository(PostType)
    private readonly postTypeRepository: Repository<PostType>,
  ) {}
  async getPostTypeByName(type: string): Promise<PostType> {
    return await this.postTypeRepository.findOne({ where: { name: type } });
  }

  async getPosts(): Promise<Post[]> {
    return await this.postRepository.find({
      order: { uploadAt: 'DESC' },
    });
  }

  async getPostsByPostType(type: PostType): Promise<Post[]> {
    return await this.postRepository.find({
      where: { postType: type },
      order: { uploadAt: 'DESC' },
    });
  }

  async getPostById(id: number): Promise<Post> {
    try {
      return await this.postRepository.findOneOrFail({
        where: { id },
        relations: ['attachedFiles'],
      });
    } catch (e) {
      if (e instanceof EntityNotFoundError) {
        throw new NotFoundException();
      } else throw e;
    }
  }

  convertFileSizeToString(size: number): string {
    if (size < 1024) {
      return `${size} B`;
    } else if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(2)} KB`;
    } else if (size < 1024 * 1024 * 1024) {
      return `${(size / 1024 / 1024).toFixed(2)} MB`;
    } else {
      return `${(size / 1024 / 1024 / 1024).toFixed(2)} GB`;
    }
  }
}
