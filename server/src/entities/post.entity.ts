import {
  Column,
  Entity,
  JoinColumn,
  ManyToOne,
  OneToMany,
  PrimaryColumn,
} from 'typeorm';
import { AttachedFile } from './attached-file.entity';
import { PostType } from './post-type.entity';

@Entity('post')
export class Post {
  @PrimaryColumn({ name: 'id', type: 'int' })
  id: number;

  @Column({ name: 'author', type: 'varchar', length: 30 })
  author: string;

  @Column({ name: 'upload_at', type: 'date' })
  uploadAt: Date;

  @Column({ name: 'title', type: 'varchar', length: 100 })
  title: string;

  @Column({ name: 'content', type: 'text', nullable: true })
  content: string;

  @ManyToOne(() => PostType)
  @JoinColumn({ name: 'post_type_id', referencedColumnName: 'id' })
  postType: PostType;

  @OneToMany(() => AttachedFile, (attachedFile) => attachedFile.post)
  attachedFiles: AttachedFile[];
}