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

  @Column({ name: 'data_key', type: 'varchar', length: 255 })
  dataKey: string;

  @Column({ name: 'name', type: 'varchar', length: 255 })
  name: string;

  @Column({ name: 'size', type: 'int', unsigned: true })
  size: number;

  @Column({ name: 'download_url', type: 'varchar', length: 255 })
  downloadUrl: string;

  @Column({ name: 'updated_at', type: 'timestamp' })
  updatedAt: Date;
}
