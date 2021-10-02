import { Column, Entity, PrimaryColumn } from 'typeorm';

@Entity('school_meal_menu')
export class SchoolMealMenu {
  @PrimaryColumn({ name: 'id', type: 'int' })
  id: number;

  @Column({ name: 'type', type: 'varchar', length: 30 })
  type: string;

  @Column({ name: 'upload_at', type: 'date' })
  uploadAt: Date;

  @Column({ name: 'title', type: 'varchar', length: 100 })
  title: string;

  @Column({ name: 'menu', type: 'varchar', length: 100 })
  menu: string;

  @Column({ name: 'image_url', type: 'varchar', length: 255, nullable: true })
  imageUrl: string;

  @Column({ name: 'updated_at', type: 'timestamp' })
  updatedAt: Date;
}
