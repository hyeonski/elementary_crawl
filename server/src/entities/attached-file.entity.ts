import {
  Column,
  Entity,
  JoinColumn,
  ManyToOne,
  PrimaryGeneratedColumn,
} from 'typeorm';
import { Post } from './post.entity';

@Entity('attached_file')
export class AttachedFile {
  @PrimaryGeneratedColumn({ name: 'id', type: 'int' })
  id: number;

  @ManyToOne(() => Post, (post) => post.attachedFiles)
  @JoinColumn({ name: 'post_id', referencedColumnName: 'id' })
  post: Post;

  @Column({ name: 'attached_file_id', type: 'varchar', length: 30 })
  attachedFileId: string;

  @Column({ name: 'file_sn', type: 'int', unsigned: true })
  fileSn: number;

  @Column({ name: 'name', type: 'varchar', length: 255 })
  name: string;

  @Column({ name: 'size', type: 'int', unsigned: true })
  size: number;
}
