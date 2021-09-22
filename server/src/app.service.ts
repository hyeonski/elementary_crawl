import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { PostType } from './entities/post-type.entity';
import { Post } from './entities/post.entity';

@Injectable()
export class AppService {
  constructor(
    @InjectRepository(Post) private readonly postRepository: Repository<Post>,
    @InjectRepository(PostType)
    private readonly postTypeRepository: Repository<PostType>,
  ) {}
  getHello(): string {
    return 'Hello World!';
  }

  async getPostTypeByName(type: string): Promise<PostType> {
    return await this.postTypeRepository.findOne({ where: { name: type } });
  }

  async getPostsByPostType(type: PostType): Promise<Post[]> {
    if (type) {
      return await this.postRepository.find({ where: { postType: type } });
    }
    return await this.postRepository.find();
  }

  getPostListViewName(type: string): string {
    if (!type) return 'index';
    const types = ['notice', 'parent_letter', 'school_meal'];
    if (types.includes(type)) {
      return type;
    }
    throw new NotFoundException();
  }
}
