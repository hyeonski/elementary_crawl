import { Column, Entity } from 'typeorm';

@Entity()
export class Post {
  @Column({ name: 'author' })
  author: string;

  @Column({ name: 'upload_at' })
  uploadAt: Date;

  @Column({ name: 'title' })
  title: string;

  @Column({ name: 'content' })
  content: string;
}
